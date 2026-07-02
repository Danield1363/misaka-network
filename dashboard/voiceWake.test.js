const assert = require("assert");
const { VoiceWakeController, extractCommandFromWakePhrase } = require("./voiceWake");

const cases = [
  ["Misaka, abra o YouTube", "abra o YouTube"],
  ["Ei Misaka abre o Discord", "abre o Discord"],
  [
    "Ok Misaka, abrir notepad no meu computador",
    "abrir notepad no meu computador",
  ],
  ["Misaka", ""],
  ["alô teste", null],
];

for (const [input, expected] of cases) {
  assert.strictEqual(extractCommandFromWakePhrase(input), expected, input);
}

const fakeStorage = {
  values: new Map(),
  getItem(key) {
    return this.values.has(key) ? this.values.get(key) : null;
  },
  setItem(key, value) {
    this.values.set(key, value);
  },
};

const sentCommands = [];
const controller = new VoiceWakeController({
  storage: fakeStorage,
  callbacks: {
    sendVoiceCommand: (command) => {
      sentCommands.push(command);
      return Promise.resolve();
    },
  },
});

controller.processTranscript("Misaka, abra o YouTube", true);
controller.processTranscript("Misaka", true);
controller.processTranscript("abrir notepad", true);

assert.deepStrictEqual(sentCommands, ["abra o YouTube", "abrir notepad"]);

console.log("voiceWake extraction tests passed");
