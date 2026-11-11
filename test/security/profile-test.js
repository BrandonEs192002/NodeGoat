/* global before, after, describe, it */
"use strict";

const config = require("../../config/config");
const assert = require("assert");
const fs = require("fs/promises");
const { Builder, By, until } = require("selenium-webdriver");
const chrome = require("selenium-webdriver/chrome");
const proxy = require("selenium-webdriver/proxy");
const ZapClient = require("zaproxy");
const target = `http://${config.hostName}:${config.port}/`;
const profile = target + "profile";
const zap = new ZapClient({
    apiKey: config.zapApiKey,
    proxy: { host: config.zapHostName, port: Number(config.zapPort), protocol: "http" }
});
let driver;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

before(async function() {
    this.timeout(60000);
    const builder = new Builder().forBrowser("chrome")
        .setProxy(proxy.manual({ http: `${config.zapHostName}:${config.zapPort}` }));
    if (process.env.CHROMEDRIVER_PATH) {
        builder.setChromeService(new chrome.ServiceBuilder(process.env.CHROMEDRIVER_PATH));
    }
    driver = await builder.build();
    await driver.get(target);
    await driver.findElement(By.name("userName")).sendKeys("user1");
    await driver.findElement(By.name("password")).sendKeys("User1_123");
    await driver.findElement(By.css("button[type=submit]")).click();
    await driver.wait(until.urlContains("dashboard"), 10000);
    await driver.get(profile);
    for (const [name, value] of Object.entries({
        firstName: "seleniumJohn", lastName: "seleniumDoe", ssn: "seleniumSSN",
        dob: "12/23/5678", bankAcc: "seleniumBankAcc", bankRouting: "0198212#", address: "seleniumAddress"
    })) {
        await driver.findElement(By.name(name)).sendKeys(value);
    }
    await driver.findElement(By.name("submit")).click();
});

after(async function() {
    this.timeout(20000);
    if (driver) await driver.quit();
    await zap.core.newSession({ name: "new NodeGoat session", overwrite: "true" });
});

describe("profile regression test suite", function() {
    this.timeout(0);
    it("Should not exceed the decided threshold of vulnerabilities known to Zap", async function() {
        const contextid = 1;
        const alertThreshold = 3;
        await zap.spider.scan({ url: target, maxchildren: 1 });
        await zap.context.includeInContext({ contextname: "Default Context", regex: "\\Q" + target + "\\E.*" });
        await zap.authentication.setAuthenticationMethod({ contextid,
            authmethodname: "formBasedAuthentication",
            authmethodconfigparams: "loginUrl=" + target + "login&loginRequestData=" +
                "userName%3D%7B%25username%25%7D%26password%3D%7B%25password%25%7D%26_csrf%3D"
        });
        await zap.authentication.setLoggedInIndicator({ contextid, loggedinindicatorregex: "\\Q/dashboard\\E" });
        await zap.forcedUser.setForcedUserModeEnabled({ boolean: "true" });
        const { userId: userid } = await zap.users.newUser({ contextid, name: "user1" });
        await zap.forcedUser.setForcedUser({ contextid, userid });
        await zap.users.setAuthenticationCredentials({ contextid, userid,
            authcredentialsconfigparams: "username=user1&password=User1_123" });
        await zap.users.setUserEnabled({ contextid, userid, enabled: "true" });
        await zap.spider.scanAsUser({ url: target, contextid, userid, maxchildren: 1 });
        const { scan: scanid } = await zap.ascan.scan({ url: profile, recurse: "true",
            inscopeonly: "false", method: "POST", postdata:
                "firstName=JohnseleniumJohn&lastName=DoeseleniumDoe&ssn=seleniumSSN&dob=12/23/5678&" +
                "bankAcc=seleniumBankAcc&bankRouting=0198212%23&address=seleniumAddress&_csrf=&submit=" });
        while (Number((await zap.ascan.status({ scanid })).status) !== 100) {
            await delay(config.zapApiFeedbackSpeed);
        }
        const { numberOfAlerts } = await zap.core.numberOfAlerts({ baseurl: profile });
        const report = await zap.core.htmlreport();
        await fs.writeFile(`${__dirname}/report_${Date.now()}.html`, report);
        assert(Number(numberOfAlerts) <= alertThreshold,
            `${numberOfAlerts} alerts exceed the existing threshold ${alertThreshold}`);
    });
});
