module.exports = {
    apps: [{
        name: 'chacha-chatbot',
        script: 'run python main.py',
        interpreter: "poetry",
        args: '--production --port=80'
    }]
};