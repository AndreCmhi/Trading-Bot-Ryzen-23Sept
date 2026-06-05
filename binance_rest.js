const crypto = require("crypto");
const https = require("https");

function request(payload) {
  const method = payload.method || "GET";
  const baseUrl = payload.baseUrl;
  const path = payload.path;
  const apiKey = payload.apiKey || "";
  const apiSecret = payload.apiSecret || "";
  const params = payload.params || {};
  const signed = Boolean(payload.signed);

  if (signed) {
    params.timestamp = Date.now();
    const queryForSig = new URLSearchParams(params).toString();
    params.signature = crypto.createHmac("sha256", apiSecret).update(queryForSig).digest("hex");
  }

  const query = new URLSearchParams(params).toString();
  const url = new URL(`${baseUrl}${path}${query ? `?${query}` : ""}`);
  const options = {
    method,
    rejectUnauthorized: false,
    headers: {
      "User-Agent": "Mozilla/5.0",
    },
  };
  if (apiKey) options.headers["X-MBX-APIKEY"] = apiKey;

  const req = https.request(url, options, (res) => {
    let data = "";
    res.on("data", (chunk) => data += chunk);
    res.on("end", () => {
      if (res.statusCode < 200 || res.statusCode >= 300) {
        process.stderr.write(JSON.stringify({ statusCode: res.statusCode, body: data.slice(0, 1000) }));
        process.exit(1);
      }
      process.stdout.write(data);
    });
  });

  req.on("error", (error) => {
    process.stderr.write(error.message);
    process.exit(1);
  });
  req.setTimeout(Number(payload.timeoutMs || 12000), () => {
    req.destroy(new Error(`Request timeout after ${Number(payload.timeoutMs || 12000)} ms`));
  });
  req.end();
}

let raw = "";
process.stdin.on("data", (chunk) => raw += chunk);
process.stdin.on("end", () => {
  try {
    request(JSON.parse(raw));
  } catch (error) {
    process.stderr.write(error.message);
    process.exit(1);
  }
});
