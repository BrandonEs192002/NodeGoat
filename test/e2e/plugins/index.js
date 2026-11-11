// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

const { port, hostName } = require("../../../config/env/all");

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)
// `on` is used to hook into various events Cypress emits
// `config` is the resolved Cypress config
module.exports = (on, config) => {
  "use strict";

  on("task", {
    "db:seed": () => new Promise((resolve, reject) => {
      const child = require("child_process").spawn(process.execPath, ["artifacts/db-reset.js"], {
        env: { ...process.env, NODE_ENV: "test" }, stdio: "ignore"
      });
      child.on("error", reject);
      child.on("close", code => code === 0 ? resolve(null) : reject(new Error("Database seed failed: " + code)));
    })
  });
  config.baseUrl = `http://${hostName}:${port}`;

  return config;
};
