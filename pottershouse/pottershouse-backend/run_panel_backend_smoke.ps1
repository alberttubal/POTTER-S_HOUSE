param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$AdminEmail = "admin@example.com",
  [string]$AdminPassword = "AdminPass123!",
  [switch]$Docker,
  [switch]$BootstrapAdmin,
  [switch]$BootstrapStorage,
  [switch]$IncludeUnitTests
)

$ErrorActionPreference = "Stop"

$PythonExe = "python"
if (Test-Path ".\venv\Scripts\python.exe") {
  $PythonExe = ".\venv\Scripts\python.exe"
}

function Invoke-BackendPython {
  param(
    [string[]]$Args
  )

  if ($Docker) {
    & docker compose exec -T web python @Args
  } else {
    & $PythonExe @Args
  }

  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
}

function Escape-PythonSingleQuoted {
  param([string]$Value)
  return $Value.Replace("\", "\\").Replace("'", "\\'")
}

function Invoke-DjangoShellScript {
  param(
    [string]$Code,
    [string]$FailureMessage
  )

  if ($Docker) {
    $Code | docker compose exec -T web python manage.py shell
  } else {
    $Code | & $PythonExe manage.py shell
  }

  if ($LASTEXITCODE -ne 0) {
    Write-Error $FailureMessage
    exit $LASTEXITCODE
  }
}

if ($BootstrapAdmin) {
  Write-Host "[RUN] Bootstrap admin user ($AdminEmail)"
  $adminEmailPy = Escape-PythonSingleQuoted $AdminEmail
  $adminPasswordPy = Escape-PythonSingleQuoted $AdminPassword
  $bootstrapCode = @"
from admin_users.models import AdminUser

email = '$adminEmailPy'
password = '$adminPasswordPy'

user, created = AdminUser.objects.get_or_create(
    email=email,
    defaults={
        "full_name": "Panel Admin",
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
    },
)
user.full_name = user.full_name or "Panel Admin"
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.set_password(password)
user.save()
print("created" if created else "updated", user.email)
"@
  Invoke-DjangoShellScript -Code $bootstrapCode -FailureMessage "Admin bootstrap failed."
}

if ($BootstrapStorage) {
  Write-Host "[RUN] Bootstrap object storage bucket"
  $storageCode = @"
from uploads.services import ensure_bucket_exists
print("bucket", ensure_bucket_exists())
"@
  Invoke-DjangoShellScript -Code $storageCode -FailureMessage "Storage bootstrap failed."
}

Write-Host "[RUN] Backend smoke checks against $BaseUrl"
Invoke-BackendPython -Args @(
  "scripts/panel_backend_smoke.py",
  "--base-url", $BaseUrl,
  "--admin-email", $AdminEmail,
  "--admin-password", $AdminPassword
)

if ($IncludeUnitTests) {
  Write-Host "[RUN] Django unit tests"
  Invoke-BackendPython -Args @("manage.py", "test", "--settings=backend.settings.test")
}

Write-Host "[PASS] Backend panel checks completed."
