const assert = require("assert");
const {
  VoiceWakeController,
  extractCommandFromWakePhrase,
  normalizeVoiceText,
} = require("./voiceWake");

assert.strictEqual(
  normalizeVoiceText("Misaka, ABRA o YouTube!"),
  "misaka abra o youtube",
);
assert.strictEqual(
  normalizeVoiceText("Ei Misaka, abrir notepad"),
  "ei misaka abrir notepad",
);

const cases = [
  ["Misaka, abra o YouTube", "abra o YouTube"],
  ["Ei Misaka abre o Discord", "abre o Discord"],
  [
    "Ok Misaka, abrir notepad no meu computador",
    "abrir notepad no meu computador",
  ],
  ["Acorda Misaka, limpe os alertas", "limpe os alertas"],
  ["Misaka", ""],
  ["alô teste", null],
  ["minha misaka não funciona", null],
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

controller.processTranscript("Misaka, abra o YouTube");
controller.processTranscript("Misaka");
assert.strictEqual(controller.state, "listening_for_command");
controller.processTranscript("abrir notepad");
controller.processTranscript("alô teste");

assert.deepStrictEqual(sentCommands, ["abra o YouTube", "abrir notepad"]);

const previousSpeechRecognition = globalThis.SpeechRecognition;

class FailingRecognition {
  start() {
    throw new Error("blocked");
  }

  stop() {}
}

globalThis.SpeechRecognition = FailingRecognition;
const startFailureStorage = {
  values: new Map(),
  getItem(key) {
    return this.values.has(key) ? this.values.get(key) : null;
  },
  setItem(key, value) {
    this.values.set(key, value);
  },
};
const startFailureController = new VoiceWakeController({
  storage: startFailureStorage,
  callbacks: {
    sendVoiceCommand: () => Promise.resolve(),
  },
});

assert.strictEqual(startFailureController.start(), false);
assert.strictEqual(startFailureController.enabled, false);
assert.strictEqual(startFailureController.state, "error");

if (previousSpeechRecognition) {
  globalThis.SpeechRecognition = previousSpeechRecognition;
} else {
  delete globalThis.SpeechRecognition;
}

console.log("voiceWake extraction tests passed");
