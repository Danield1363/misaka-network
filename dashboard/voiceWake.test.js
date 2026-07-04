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
    constructor(stream, options = {}) {
      this.stream = stream;
      this.mimeType = options.mimeType || "audio/webm";
      this.state = "inactive";
      this.ondataavailable = null;
      this.onerror = null;
      this.onstop = null;
    }

    static isTypeSupported() {
      return true;
    }

    start() {
      this.state = "recording";
    }

    requestData() {
      if (this.ondataavailable) {
        this.ondataavailable({
          data: new Blob(["fake-audio"], { type: this.mimeType }),
        });
      }
    }

    stop() {
      if (this.state === "inactive") return;
      this.requestData();
      this.state = "inactive";
      setTimeout(() => {
        if (this.onstop) this.onstop();
      }, 0);
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
  const ignoredCommands = [];
  const controller = new VoiceWakeController({
    storage: fakeStorage(),
    callbacks: {
      onCommand: (command) => {
        commands.push(command);
        return Promise.resolve({ success: true });
      },
      onCommandIgnored: (command, reason) => {
        ignoredCommands.push({ command, reason });
      },
    },
  });
  await controller.init();
  controller.chunkMs = 10;
  controller.commandCooldownMs = 15000;
  controller.stream = {
    getTracks: () => [{ stop: () => {} }],
  };
  controller.mediaStream = controller.stream;
  controller.enabled = true;

  const blob = await controller.recordChunk();
  assert.ok(blob);
  assert.ok(blob.size > 0);
  assert.strictEqual(controller.recording, false);

  const result = await controller.sendAudioForTranscription(blob);

  assert.strictEqual(result.success, true);
  assert.strictEqual(result.text, "abrir youtube");
  const firstCommand = await controller.processVoiceText(result.text);
  assert.strictEqual(firstCommand.executed, true);
  assert.deepStrictEqual(commands, ["abrir youtube"]);

  const duplicateOne = await controller.processVoiceText("abrir youtube");
  const duplicateTwo = await controller.processVoiceText("abrir youtube");
  assert.strictEqual(duplicateOne.executed, false);
  assert.strictEqual(duplicateOne.reason, "duplicate_cooldown");
  assert.strictEqual(duplicateTwo.executed, false);
  assert.deepStrictEqual(commands, ["abrir youtube"]);
  assert.strictEqual(ignoredCommands.length, 2);

  controller.lastExecutedVoiceCommandAt = Date.now() - 16000;
  const afterCooldown = await controller.processVoiceText("abrir youtube");
  assert.strictEqual(afterCooldown.executed, true);
  assert.deepStrictEqual(commands, ["abrir youtube", "abrir youtube"]);

  controller.processingCommand = true;
  const whileProcessing = await controller.processVoiceText("abrir discord");
  assert.strictEqual(whileProcessing.executed, false);
  assert.strictEqual(whileProcessing.reason, "processing");
  assert.deepStrictEqual(commands, ["abrir youtube", "abrir youtube"]);
  controller.processingCommand = false;

  let resolveCommand;
  const awaitedCommands = [];
  const awaitedController = new VoiceWakeController({
    storage: fakeStorage(),
    callbacks: {
      onCommand: (command) => {
        awaitedCommands.push(command);
        return new Promise((resolve) => {
          resolveCommand = resolve;
        });
      },
    },
  });
  await awaitedController.init();
  const pendingCommand = awaitedController.processVoiceText("abrir explorer");
  await Promise.resolve();
  assert.strictEqual(awaitedController.processingCommand, true);
  resolveCommand({ success: true });
  const awaitedResult = await pendingCommand;
  assert.strictEqual(awaitedResult.executed, true);
  assert.strictEqual(awaitedController.processingCommand, false);
  assert.deepStrictEqual(awaitedCommands, ["abrir explorer"]);

  const powerCommands = [];
  const powerController = new VoiceWakeController({
    storage: fakeStorage(),
    callbacks: {
      onCommand: (command) => {
        powerCommands.push(command);
        return Promise.resolve({ success: true });
      },
    },
  });
  await powerController.init();
  const powerResult = await powerController.processVoiceText(
    "desligar computador",
  );
  assert.strictEqual(powerResult.executed, true);
  assert.deepStrictEqual(powerCommands, ["desligar computador"]);

  await controller.stop();
  assert.strictEqual(controller.listeningLoopActive, false);
  assert.strictEqual(controller.recording, false);

  const loopCommands = [];
  const loopIgnoredCommands = [];
  const debugMessages = [];
  const loopController = new VoiceWakeController({
    storage: fakeStorage(),
    callbacks: {
      onCommand: (command) => {
        loopCommands.push(command);
        return Promise.resolve({ success: true });
      },
      onCommandIgnored: (command, reason) => {
        loopIgnoredCommands.push({ command, reason });
      },
      onDebug: (message) => {
        debugMessages.push(message);
      },
    },
  });
  loopController.chunkMs = 10;
  loopController.postCommandPauseMs = 20;
  loopController.commandCooldownMs = 15000;
  await loopController.init();
  const startResult = await loopController.start();
  assert.strictEqual(startResult.success, true);
  loopController.startListeningLoop();
  await new Promise((resolve) => setTimeout(resolve, 120));
  assert.deepStrictEqual(loopCommands, ["abrir youtube"]);
  assert.ok(
    loopIgnoredCommands.some(
      (entry) =>
        entry.command === "abrir youtube" &&
        entry.reason === "duplicate_cooldown",
    ),
  );
  assert.ok(
    debugMessages.some((message) =>
      String(message).includes("Listening loop already active"),
    ),
  );
  await loopController.stop();
  assert.strictEqual(loopController.recording, false);
  assert.strictEqual(loopController.transcribing, false);
  assert.strictEqual(loopController.enabled, false);

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

async function runStopCancellationTest() {
  let recorderStopped = false;
  let trackStopped = false;
  let abortSeen = false;
  const abortController = new AbortController();
  abortController.signal.addEventListener("abort", () => {
    abortSeen = true;
  });

  const controller = new VoiceWakeController({ storage: fakeStorage() });
  controller.abortController = abortController;
  controller.currentRecorder = {
    state: "recording",
    stop: () => {
      recorderStopped = true;
    },
  };
  controller.currentStream = {
    getTracks: () => [
      {
        stop: () => {
          trackStopped = true;
        },
      },
    ],
  };
  controller.recordingTimer = setTimeout(() => {}, 1000);
  controller.hardTimeout = setTimeout(() => {}, 1000);
  controller.loopTimer = setTimeout(() => {}, 1000);
  controller.enabled = true;
  controller.listeningLoopActive = true;
  controller.recording = true;
  controller.transcribing = true;
  controller.processingCommand = true;

  const result = await controller.stop();

  assert.strictEqual(result.success, true);
  assert.strictEqual(result.stopped, true);
  assert.strictEqual(controller.enabled, false);
  assert.strictEqual(controller.listeningLoopActive, false);
  assert.strictEqual(controller.recording, false);
  assert.strictEqual(controller.transcribing, false);
  assert.strictEqual(controller.processingCommand, false);
  assert.strictEqual(recorderStopped, true);
  assert.strictEqual(trackStopped, true);
  assert.strictEqual(abortSeen, true);
  assert.strictEqual(controller.recordingTimer, null);
  assert.strictEqual(controller.hardTimeout, null);
  assert.strictEqual(controller.loopTimer, null);
}

runCloudVoiceTests()
  .then(runStartFailureTest)
  .then(runStopCancellationTest)
  .then(() => {
    console.log("all voiceWake tests passed");
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
