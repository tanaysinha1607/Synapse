// make_jwks.js
// Run with: node make_jwks.js
const fs = require("fs");
const { importSPKI, exportJWK } = require("jose");

(async () => {
  try {
    const pem = fs.readFileSync("../jwt_public.pem", "utf8");
    // RS256 is the typical alg used for RSA keys in JWTs
    const key = await importSPKI(pem, "RS256");
    const jwk = await exportJWK(key);
    // Add recommended JWKS properties
    jwk.kid = jwk.kid || "synapse-key-1";
    jwk.use = "sig";
    jwk.alg = "RS256";
    const jwks = { keys: [jwk] };
    console.log(JSON.stringify(jwks));
  } catch (err) {
    console.error("Error:", err.message);
    process.exit(1);
  }
})();
