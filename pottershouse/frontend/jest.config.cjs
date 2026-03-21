module.exports = {
  testEnvironment: "jest-environment-jsdom",
  setupFilesAfterEnv: ["<rootDir>/src/test/setup.ts"],
  transform: {
    "^.+\\.(ts|tsx)$": ["ts-jest", { tsconfig: "<rootDir>/tsconfig.json" }]
  },
  moduleNameMapper: {
    "\\.(css|less|scss)$": "identity-obj-proxy"
  },
  testMatch: ["<rootDir>/src/test/**/*.spec.(ts|tsx)"]
};
