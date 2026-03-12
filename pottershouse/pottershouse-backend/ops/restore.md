# Restore Guide 

This restores a dump created by ops/backup.sh. 

## Example 

pg_restore -h <host> -U <user> -d pottershouse_prod /backups/pottershouse_2026-03-01.dump 

## Notes 
- Ensure the target database exists. 
- Provide PGPASSWORD env var or .pgpass for auth. 
- Run from a trusted network / bastion. 
