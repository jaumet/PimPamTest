(function () {
  var storageKey = "pimpamtest-sound";
  var audioContext = null;
  var soundEnabled = localStorage.getItem(storageKey) !== "off";

  function getAudioContext() {
    if (!audioContext) {
      var AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) return null;
      audioContext = new AudioContextClass();
    }
    if (audioContext.state === "suspended") {
      audioContext.resume();
    }
    return audioContext;
  }

  function playTone(frequency, start, duration, type, gainValue) {
    var context = getAudioContext();
    if (!context) return;

    var oscillator = context.createOscillator();
    var gain = context.createGain();
    oscillator.type = type || "sine";
    oscillator.frequency.setValueAtTime(frequency, context.currentTime + start);
    gain.gain.setValueAtTime(0.0001, context.currentTime + start);
    gain.gain.exponentialRampToValueAtTime(gainValue || 0.08, context.currentTime + start + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + start + duration);
    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start(context.currentTime + start);
    oscillator.stop(context.currentTime + start + duration + 0.03);
  }

  function playSlide(from, to, start, duration, type, gainValue) {
    var context = getAudioContext();
    if (!context) return;

    var oscillator = context.createOscillator();
    var gain = context.createGain();
    oscillator.type = type || "triangle";
    oscillator.frequency.setValueAtTime(from, context.currentTime + start);
    oscillator.frequency.exponentialRampToValueAtTime(to, context.currentTime + start + duration);
    gain.gain.setValueAtTime(0.0001, context.currentTime + start);
    gain.gain.exponentialRampToValueAtTime(gainValue || 0.08, context.currentTime + start + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + start + duration);
    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start(context.currentTime + start);
    oscillator.stop(context.currentTime + start + duration + 0.04);
  }

  function say(text, pitch, rate, delay) {
    if (!("speechSynthesis" in window)) return;
    window.setTimeout(function () {
      if (!soundEnabled) return;
      var utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "ca-ES";
      utterance.pitch = pitch;
      utterance.rate = rate;
      utterance.volume = 0.75;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    }, delay || 0);
  }

  function playSound(name) {
    if (!soundEnabled) return;

    if (name === "option") {
      playTone(660, 0, 0.08, "triangle", 0.05);
      playTone(880, 0.045, 0.09, "triangle", 0.045);
      return;
    }

    if (name === "submit") {
      playTone(440, 0, 0.08, "square", 0.045);
      playTone(660, 0.07, 0.09, "square", 0.05);
      playTone(990, 0.15, 0.13, "triangle", 0.06);
      return;
    }

    if (name === "move") {
      playSlide(420, 760, 0, 0.12, "triangle", 0.04);
      return;
    }

    if (name === "pimpam") {
      playTone(523.25, 0, 0.12, "triangle", 0.08);
      playTone(659.25, 0.09, 0.13, "triangle", 0.08);
      playTone(783.99, 0.18, 0.18, "triangle", 0.085);
      playTone(1046.5, 0.36, 0.28, "sine", 0.09);
      say("Pim Pam!", 1.35, 1.05, 220);
      return;
    }

    if (name === "demon") {
      playSlide(260, 95, 0, 0.75, "sawtooth", 0.075);
      playTone(130, 0.2, 0.2, "square", 0.035);
      say("Ooooh!", 0.65, 0.85, 180);
      return;
    }
  }

  function updateSoundButton(button) {
    button.classList.toggle("is-muted", !soundEnabled);
    button.setAttribute("aria-pressed", soundEnabled ? "false" : "true");
    button.setAttribute("aria-label", soundEnabled ? "Silenciar sons" : "Activar sons");
    button.title = soundEnabled ? "Silenciar sons" : "Activar sons";
  }

  function setupToggle() {
    var button = document.querySelector("[data-sound-toggle]");
    if (!button) return;
    updateSoundButton(button);
    button.addEventListener("click", function () {
      soundEnabled = !soundEnabled;
      localStorage.setItem(storageKey, soundEnabled ? "on" : "off");
      updateSoundButton(button);
      if (soundEnabled) {
        playSound("option");
      } else if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    });
  }

  function setupInteractionSounds() {
    document.addEventListener("click", function (event) {
      var element = event.target.closest("[data-sound]");
      if (!element) return;
      playSound(element.dataset.sound || "option");
    });

    document.addEventListener("change", function (event) {
      if (event.target.matches('input[type="radio"][data-sound]')) {
        playSound(event.target.dataset.sound || "option");
      }
    });

    document.addEventListener("focusin", function (event) {
      if (event.target.matches("[data-sound-focus]")) {
        playSound("option");
      }
    });
  }

  function setupResultSound() {
    var celebration = document.querySelector("[data-celebration][data-result-sound]");
    if (!celebration) return;
    function playResultSoundOnce() {
      playSound(celebration.dataset.resultSound);
    }
    window.setTimeout(function () {
      playResultSoundOnce();
    }, 260);
    celebration.addEventListener("click", playResultSoundOnce, { once: true });
  }

  setupToggle();
  setupInteractionSounds();
  setupResultSound();
})();
