module.exports = {
    apps: [{
        name: 'llmchat-for-child',
        script: 'main.py',
        interpreter: "python3",
        args: '--production --port=80'
    }]
};