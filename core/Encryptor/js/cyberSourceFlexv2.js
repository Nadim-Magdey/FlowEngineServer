const { encrypt } = require('cs2-encryption');

async function encryptCard(data, context) {
    try {
        const encrypted = await encrypt(data, context);
        console.log(JSON.stringify(encrypted)); // IMPORTANT
    } catch (error) {
        console.error(JSON.stringify({
            error: error.message || String(error)
        }));
        process.exit(1);
    }
}

const args = process.argv.slice(2);
// [context, number, securityCode, expirationMonth, expirationYear, type]

const context = args[0];
const data = {
    number: args[1],
    securityCode: args[2],
    expirationMonth: args[3],
    expirationYear: args[4],
    type: args[5],
};

encryptCard(data, context);
