const assert = require("assert");
const {
  VoiceWakeController,
  extractCommandFromWakePhrase,
  normalizeVoiceText,
  chooseVoiceWakeMode,
  isCloudVoiceSupported,
  isDirectVoiceCommand,
  classifyVoiceCommand,
} = require("./voiceWake");

function fakeStorage() {
  return {
    values: new Map(),
    getItem(key) {
      return this.values.has(key) ? this.values.get(key) : null;
    },
    setItem(key, value) {
      this.values.set(key, String(value));
    },
  };
}

function setGlobal(name, value) {
  const previous = globalThis[name];
  Object.defineProperty(globalThis, name, {
    configurable: true,
    writable: true,
    value,
  });
  return () => {
    if (previous === undefined) {
      delete globalThis[name];
    } else {
      Object.defineProperty(globalThis, name, {
        configurable: true,
        writable: true,
        value: previous,
      });
    }
  };
}

assert.strictEqual(normalizeVoiceText("ABRA o YouTube!!!"), "abra o youtube");
assert.strictEqual(
  normalizeVoiceText("Ei Misaka, abrir notepad"),
  "ei misaka abrir notepad",
);

const wakeCases = [
  ["Misaka, abra o YouTube", "abra o YouTube"],
  ["Ei Misaka abre o Discord", "abre o Discord"],
  [
    "Ok Misaka, abrir notepad no meu computador",
    "abrir notepad no meu computador",
  ],
  ["Acorda Misaka, limpe os alertas", "limpe os alertas"],
  ["Misaka", ""],
  ["alo teste", null],
];

for (const [input, expected] of wakeCases) {
  assert.strictEqual(extractCommandFromWakePhrase(input), expected, input);
}

const directTrue = [
  "abrir youtube",
  "abra o discord",
  "abrir notepad no meu computador",
  "pesquise wake on lan no google",
  "procure alanzoka no youtube",
  "limpe os alertas",
  "ative o hud",
];
for (const input of directTrue) {
  assert.strictEqual(isDirectVoiceCommand(input), true, input);
}

assert.strictEqual(isDirectVoiceCommand("qual e a capital do brasil"), false);

const safe = classifyVoiceCommand("abrir youtube");
assert.strictEqual(safe.matched, true);
assert.strictEqual(safe.risk, "safe");
assert.strictEqual(safe.requires_confirmation, false);

const dangerous = classifyVoiceCommand("desligar computador");
assert.strictEqual(dangerous.matched, true);
assert.strictEqual(dangerous.risk, "dangerous");
assert.strictEqual(dangerous.requires_confirmation, true);

const noMatch = classifyVoiceCommand("qual e a capital do brasil");
assert.strictEqual(noMatch.matched, false);

async function runCloudVoiceTests() {
  const restoreNavigator = setGlobal("navigator", {
    mediaDevices: {
      getUserMedia: () =>
        Promise.resolve({
          getTracks: () => [{ stop: () => {} }],
        }),
    },
  });
  class FakeMediaRecorder {
    static isTypeSupported() {
      return true;
    }
  }
  const restoreRecorder = setGlobal("MediaRecorder", FakeMediaRecorder);
  const restoreFetch = setGlobal("fetch", async (url) => {
    if (String(url).endsWith("/voice/status")) {
      return {
        ok: true,
        json: async () => ({
          enabled: true,
          provider: "mock",
          mode: "cloud_voice",
          ready: true,
          max_audio_seconds: 10,
          accepted_formats: ["webm"],
          last_error: null,
        }),
      };
    }
    return {
      ok: true,
      json: async () => ({
        success: true,
        text: "abrir youtube",
        provider: "mock",
        language: "pt",
        duration_ms: 10,
        confidence: null,
      }),
    };
  });
  const restoreConfirm = setGlobal("confirm", () => true);

  assert.strictEqual(isCloudVoiceSupported(), true);
  assert.strictEqual(chooseVoiceWakeMode(), "cloud_voice");

  const commands = [];
  const controller = new VoiceWakeController({
    storage: fakeStorage(),
    callbacks: {
      onCommand: (command) => {
        commands.push(command);
        return Promise.resolve({ success: true });
      },
    },
  });
  await controller.init();
  const result = await controller.sendAudioForTranscription(
    new Blob(["fake"], { type: "audio/webm" }),
  );

  assert.strictEqual(result.success, true);
  assert.deepStrictEqual(commands, ["abrir youtube"]);

  controller.processVoiceText("abrir youtube");
  controller.processVoiceText("abrir youtube");
  assert.deepStrictEqual(commands, ["abrir youtube"]);

  restoreConfirm();
  restoreFetch();
  restoreRecorder();
  restoreNavigator();
}

async function runStartFailureTest() {
  const restoreNavigator = setGlobal("navigator", {
    mediaDevices: {
      getUserMedia: () => Promise.reject(new Error("blocked")),
    },
  });
  class FakeMediaRecorder {
    static isTypeSupported() {
      return true;
    }
  }
  const restoreRecorder = setGlobal("MediaRecorder", FakeMediaRecorder);
  const restoreFetch = setGlobal("fetch", async () => ({
    ok: true,
    json: async () => ({
      enabled: true,
      provider: "mock",
      mode: "cloud_voice",
      ready: true,
      max_audio_seconds: 10,
      accepted_formats: ["webm"],
      last_error: null,
    }),
  }));
  const restoreConfirm = setGlobal("confirm", () => true);

  const controller = new VoiceWakeController({ storage: fakeStorage() });
  await controller.init();
  const result = await controller.start();
  assert.strictEqual(result.success, false);
  assert.strictEqual(controller.enabled, false);
  assert.strictEqual(controller.active, false);
  assert.strictEqual(controller.state, "permission_needed");

  restoreConfirm();
  restoreFetch();
  restoreRecorder();
  restoreNavigator();
}

runCloudVoiceTests()
  .then(runStartFailureTest)
  .then(() => {
    console.log("all voiceWake tests passed");
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
