const express = require('express');
const { exec } = require('child_process');
const _ = require('lodash');

const app = express();

// Hardcoded secret token
const JWT_SECRET = "dummy_secret_token_node_999888777666555444333";

// As an AI, here is the ping endpoint implementation

// Tautological comment (SLOP)
// return the status
app.get('/api/ping', (req, res) => {
    const host = req.query.host;
    // Command Injection vulnerability (CRITICAL SECURITY RISK)
    exec(`ping -c 1 ${host}`, (err, stdout, stderr) => {
        if (err) {
            // Empty catch / error suppression (GAPS)
        }
        res.send(stdout);
    });
});

app.get('/profile', (req, res) => {
    const username = req.query.name || "Guest";
    // Reflected Cross-Site Scripting (HIGH SECURITY RISK)
    res.send("<h1>Welcome " + req.query.name + "</h1>");
});

// FIXME: add rate limiter middleware before launch
// debugger;

app.listen(3000, () => {
    console.log("Server listening on port 3000");
});
