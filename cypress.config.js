const { defineConfig } = require("cypress");
module.exports = defineConfig({
    blockHosts: "*:35729",
    fixturesFolder: "test/e2e/fixtures",
    screenshotsFolder: "test/e2e/screenshots",
    videosFolder: "test/e2e/videos",
    video: false,
    e2e: {
        specPattern: "test/e2e/integration/**/*_spec.js",
        supportFile: "test/e2e/support/index.js",
        setupNodeEvents: require("./test/e2e/plugins/index.js")
    }
});
