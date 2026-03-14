const fs = require('fs');
const path = require('path');

// Define test scripts for different endpoint types
const testScripts = {
  // Health check endpoint
  healthCheck: `pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});

pm.test("Response has expected structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.be.an("object");
});`,

  // GET list endpoints (public)
  getListPublic: `pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});

pm.test("Response has results array", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.be.an("array").or.to.have.property("results");
});`,

  // GET list endpoints (admin)
  getListAdmin: `pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});

pm.test("Response has results array", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.be.an("array").or.to.have.property("results");
});`,

  // GET single item endpoints
  getSingle: `pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});

pm.test("Response has id field", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("id");
});`,

  // POST create endpoints (201 Created)
  postCreate: `pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});

pm.test("Response has id field", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("id");
});`,

  // POST create booking (201 Created)
  postCreateBooking: `pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});

pm.test("Response has booking id", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("id");
});`,

  // POST login endpoint
  postLogin: `pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});

pm.test("Response has access token", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("access");
});

pm.test("Response has refresh token", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("refresh");
});

// Save bearer token for subsequent requests
if (pm.response.code === 200) {
    const jsonData = pm.response.json();
    pm.environment.set("bearerToken", jsonData.access);
}`,

  // POST refresh endpoint
  postRefresh: `pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});

pm.test("Response has access token", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("access");
});

// Save bearer token for subsequent requests
if (pm.response.code === 200) {
    const jsonData = pm.response.json();
    pm.environment.set("bearerToken", jsonData.access);
}`,

  // POST forgot password
  postForgotPassword: `pm.test("Status code is 200 or 204", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 204]);
});`,

  // POST reset password
  postResetPassword: `pm.test("Status code is 200 or 204", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 204]);
});`,

  // PUT/PATCH update endpoints
  putPatchUpdate: `pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});

pm.test("Response has id field", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("id");
});`,

  // DELETE endpoints
  deleteEndpoint: `pm.test("Status code is 204", function () {
    pm.response.to.have.status(204);
});`,

  // CSV export
  csvExport: `pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is CSV", function () {
    pm.response.to.have.header("Content-Type", /text\\/csv/);
});`,

  // POST upload files
  postUpload: `pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response is JSON", function () {
    pm.response.to.have.header("Content-Type", /application\\/json/);
});`
};

// File configurations with their test types
const fileConfigs = [
  // Public endpoints
  { path: 'postman/collections/Potters House API/health/Health check.request.yaml', testType: 'healthCheck', insertAfterLine: 8 },
  { path: 'postman/collections/Potters House API/packages/List packages.request.yaml', testType: 'getListPublic', insertAfterLine: 12 },
  { path: 'postman/collections/Potters House API/packages/{id}/Get package.request.yaml', testType: 'getSingle', insertAfterLine: 10 },
  { path: 'postman/collections/Potters House API/bookings/Create booking.request.yaml', testType: 'postCreateBooking', insertAfterLine: 23 },
  { path: 'postman/collections/Potters House API/testimonials/List testimonials.request.yaml', testType: 'getListPublic', insertAfterLine: 8 },
  { path: 'postman/collections/Potters House API/faqs/List faqs.request.yaml', testType: 'getListPublic', insertAfterLine: 8 },
  { path: 'postman/collections/Potters House API/gallery/List gallery.request.yaml', testType: 'getListPublic', insertAfterLine: 8 },
  
  // Admin Auth endpoints
  { path: 'postman/collections/Potters House API/admin/login/Admin login.request.yaml', testType: 'postLogin', insertAfterLine: 13 },
  { path: 'postman/collections/Potters House API/admin/refresh/Admin refresh.request.yaml', testType: 'postRefresh', insertAfterLine: 12 },
  { path: 'postman/collections/Potters House API/admin/password/forgot/Admin password forgot.request.yaml', testType: 'postForgotPassword', insertAfterLine: 12 },
  { path: 'postman/collections/Potters House API/admin/password/reset/Admin password reset.request.yaml', testType: 'postResetPassword', insertAfterLine: 14 },
  
  // Admin Bookings
  { path: 'postman/collections/Potters House API/admin/bookings/List bookings (admin).request.yaml', testType: 'getListAdmin', insertAfterLine: 15, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/bookings/{id}/Get booking (admin).request.yaml', testType: 'getSingle', insertAfterLine: 10, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/bookings/{id}/Update booking (admin).request.yaml', testType: 'putPatchUpdate', insertAfterLine: 27, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/bookings/{id}/Update booking (admin) 1.request.yaml', testType: 'putPatchUpdate', insertAfterLine: 28, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/bookings.csv/Export bookings CSV (admin).request.yaml', testType: 'csvExport', insertAfterLine: 8, hasAuth: true },
  
  // Admin Packages
  { path: 'postman/collections/Potters House API/admin/packages/List packages (admin).request.yaml', testType: 'getListAdmin', insertAfterLine: 8, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/packages/Create package.request.yaml', testType: 'postCreate', insertAfterLine: 15, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/packages/{id}/Get package (admin).request.yaml', testType: 'getSingle', insertAfterLine: 10, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/packages/{id}/Update package.request.yaml', testType: 'putPatchUpdate', insertAfterLine: 17, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/packages/{id}/Update package 1.request.yaml', testType: 'putPatchUpdate', insertAfterLine: 18, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/packages/{id}/Delete package.request.yaml', testType: 'deleteEndpoint', insertAfterLine: 10, hasAuth: true },
  
  // Admin FAQs
  { path: 'postman/collections/Potters House API/admin/faqs/List faqs (admin).request.yaml', testType: 'getListAdmin', insertAfterLine: 8, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/faqs/Create faq (admin).request.yaml', testType: 'postCreate', insertAfterLine: 14, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/faqs/{id}/Get faq (admin).request.yaml', testType: 'getSingle', insertAfterLine: 10, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/faqs/{id}/Update faq (admin).request.yaml', testType: 'putPatchUpdate', insertAfterLine: 16, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/faqs/{id}/Update faq (admin) 1.request.yaml', testType: 'putPatchUpdate', insertAfterLine: 17, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/faqs/{id}/Delete faq (admin).request.yaml', testType: 'deleteEndpoint', insertAfterLine: 10, hasAuth: true },
  
  // Admin Testimonials
  { path: 'postman/collections/Potters House API/admin/testimonials/List testimonials (admin).request.yaml', testType: 'getListAdmin', insertAfterLine: 8, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/testimonials/Create testimonial (admin).request.yaml', testType: 'postCreate', insertAfterLine: 14, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/testimonials/{id}/Get testimonial (admin).request.yaml', testType: 'getSingle', insertAfterLine: 10, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/testimonials/{id}/Update testimonial (admin).request.yaml', testType: 'putPatchUpdate', insertAfterLine: 16, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/testimonials/{id}/Update testimonial (admin) 1.request.yaml', testType: 'putPatchUpdate', insertAfterLine: 17, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/testimonials/{id}/Delete testimonial (admin).request.yaml', testType: 'deleteEndpoint', insertAfterLine: 10, hasAuth: true },
  
  // Admin Settings
  { path: 'postman/collections/Potters House API/admin/settings/List settings (admin).request.yaml', testType: 'getListAdmin', insertAfterLine: 8, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/settings/Create setting (admin).request.yaml', testType: 'postCreate', insertAfterLine: 13, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/settings/{id}/Get setting (admin).request.yaml', testType: 'getSingle', insertAfterLine: 10, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/settings/{id}/Update setting (admin).request.yaml', testType: 'putPatchUpdate', insertAfterLine: 15, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/settings/{id}/Update setting (admin) 1.request.yaml', testType: 'putPatchUpdate', insertAfterLine: 16, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/settings/{id}/Delete setting (admin).request.yaml', testType: 'deleteEndpoint', insertAfterLine: 10, hasAuth: true },
  
  // Admin Uploads
  { path: 'postman/collections/Potters House API/admin/uploads/list/List uploads (admin).request.yaml', testType: 'getListAdmin', insertAfterLine: 8, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/uploads/Upload files (admin).request.yaml', testType: 'postUpload', insertAfterLine: 13, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/uploads/{id}/Get upload (admin).request.yaml', testType: 'getSingle', insertAfterLine: 10, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/uploads/{id}/Update upload (admin).request.yaml', testType: 'putPatchUpdate', insertAfterLine: 15, hasAuth: true },
  { path: 'postman/collections/Potters House API/admin/uploads/{id}/Update upload (admin) 1.request.yaml', testType: 'putPatchUpdate', insertAfterLine: 16, hasAuth: true }
];

function addTestsToFile(filePath, testType) {
  const fullPath = path.join(process.cwd(), filePath);
  
  if (!fs.existsSync(fullPath)) {
    console.log(`File not found: ${filePath}`);
    return false;
  }
  
  let content = fs.readFileSync(fullPath, 'utf8');
  
  // Check if tests already exist
  if (content.includes('scripts:') || content.includes('tests:')) {
    console.log(`Tests already exist in: ${filePath}`);
    return false;
  }
  
  const testScript = testScripts[testType];
  if (!testScript) {
    console.log(`Unknown test type: ${testType}`);
    return false;
  }
  
  // Find where to insert the tests block (before auth: or examples: or order:)
  const lines = content.split('\n');
  let insertIndex = -1;
  
  // Find the first occurrence of auth:, examples:, or order: at root level
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.match(/^auth:/) || line.match(/^examples:/) || line.match(/^order:/)) {
      insertIndex = i;
      break;
    }
  }
  
  if (insertIndex === -1) {
    // Insert at the end if no marker found
    insertIndex = lines.length;
  }
  
  // Create the scripts block with proper YAML formatting
  const scriptsBlock = `scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
${testScript.split('\n').map(line => '      ' + line).join('\n')}`;
  
  // Insert the scripts block
  lines.splice(insertIndex, 0, scriptsBlock);
  
  const newContent = lines.join('\n');
  fs.writeFileSync(fullPath, newContent, 'utf8');
  console.log(`Updated: ${filePath}`);
  return true;
}

// Process all files
let successCount = 0;
let failCount = 0;

for (const config of fileConfigs) {
  const result = addTestsToFile(config.path, config.testType);
  if (result) {
    successCount++;
  } else {
    failCount++;
  }
}

console.log(`\nCompleted: ${successCount} files updated, ${failCount} files skipped/failed`);
