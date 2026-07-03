const assert = require("assert");
const {
  VoiceWakeController,
  extractCommandFromWakePhrase,
  normalizeVoiceText,
  chooseVoiceWakeMode,
  isWebSpeechSupported,
  isNativeDesktopSupported,
  isDirectVoiceCommand,
  classifyVoiceCommand,
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

// start() is now async — test it with .then()
startFailureController.start().then((result) => {
  assert.strictEqual(result.success, false);
  assert.strictEqual(startFailureController.enabled, false);
  assert.strictEqual(startFailureController.state, "error");

  if (previousSpeechRecognition) {
    globalThis.SpeechRecognition = previousSpeechRecognition;
  } else {
    delete globalThis.SpeechRecognition;
  }

  runModeSelectionTests();
});

// --- Direct command tests ---

function runDirectCommandTests() {
  // isDirectVoiceCommand
  assert.strictEqual(isDirectVoiceCommand("abrir youtube"), true);
  assert.strictEqual(isDirectVoiceCommand("abra o discord"), true);
  assert.strictEqual(isDirectVoiceCommand("abrir notepad no meu computador"), true);
  assert.strictEqual(isDirectVoiceCommand("pesquise wake on lan no google"), true);
  assert.strictEqual(isDirectVoiceCommand("procure alanzoka no youtube"), true);
  assert.strictEqual(isDirectVoiceCommand("limpe os alertas"), true);
  assert.strictEqual(isDirectVoiceCommand("ative o hud"), true);
  assert.strictEqual(isDirectVoiceCommand("qual e a capital do brasil"), false);
  assert.strictEqual(isDirectVoiceCommand("como vai voce"), false);
  assert.strictEqual(isDirectVoiceCommand(""), false);

  // classifyVoiceCommand - safe
  const safe1 = classifyVoiceCommand("abrir youtube");
  assert.strictEqual(safe1.matched, true);
  assert.strictEqual(safe1.risk, "safe");
  assert.strictEqual(safe1.requires_confirmation, false);

  const safe2 = classifyVoiceCommand("pesquise wake on lan no google");
  assert.strictEqual(safe2.matched, true);
  assert.strictEqual(safe2.risk, "safe");

  const safe3 = classifyVoiceCommand("limpe os alertas");
  assert.strictEqual(safe3.matched, true);
  assert.strictEqual(safe3.risk, "safe");

  // classifyVoiceCommand - dangerous
  const dangerous1 = classifyVoiceCommand("desligar computador");
  assert.strictEqual(dangerous1.matched, true);
  assert.strictEqual(dangerous1.risk, "dangerous");
  assert.strictEqual(dangerous1.requires_confirmation, true);

  const dangerous2 = classifyVoiceCommand("reiniciar pc");
  assert.strictEqual(dangerous2.matched, true);
  assert.strictEqual(dangerous2.risk, "dangerous");

  const dangerous3 = classifyVoiceCommand("formatar");
  assert.strictEqual(dangerous3.matched, true);
  assert.strictEqual(dangerous3.risk, "dangerous");

  // classifyVoiceCommand - not matched
  const nomatch = classifyVoiceCommand("qual e a capital do brasil");
  assert.strictEqual(nomatch.matched, false);

  console.log("direct command tests passed");
}

runDirectCommandTests();

// --- Mode selection tests ---

function runModeSelectionTests() {
  const prevSR = globalThis.SpeechRecognition;
  const prevWebkit = globalThis.webkitSpeechRecognition;
  const prevDesktop = globalThis.misakaDesktop;

  // Test: Web Speech available -> web_speech
  class FakeRecognition { start() {} stop() {} }
  globalThis.SpeechRecognition = FakeRecognition;
  assert.strictEqual(chooseVoiceWakeMode(), "web_speech");
  assert.strictEqual(isWebSpeechSupported(), true);

  // Test: Web Speech unavailable + native available -> native_desktop
  delete globalThis.SpeechRecognition;
  delete globalThis.webkitSpeechRecognition;
  globalThis.misakaDesktop = {
    isAvailable: true,
    nativeVoiceIsAvailable: () => true,
    nativeVoiceStart: () => Promise.resolve({ success: true }),
    nativeVoiceStop: () => Promise.resolve({ success: true }),
  };
  assert.strictEqual(chooseVoiceWakeMode(), "native_desktop");
  assert.strictEqual(isNativeDesktopSupported(), true);

  // Test: Nothing available -> unavailable
  delete globalThis.misakaDesktop;
  assert.strictEqual(chooseVoiceWakeMode(), "unavailable");

  // Restore globals
  if (prevSR) globalThis.SpeechRecognition = prevSR;
  else delete globalThis.SpeechRecognition;
  if (prevWebkit) globalThis.webkitSpeechRecognition = prevWebkit;
  else delete globalThis.webkitSpeechRecognition;
  if (prevDesktop) globalThis.misakaDesktop = prevDesktop;
  else delete globalThis.misakaDesktop;

  console.log("voiceWake extraction tests passed");
}
