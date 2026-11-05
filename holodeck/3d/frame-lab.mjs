/**
 * Frame timing, deterministic simulation stepping, and bounded frame capture.
 * Rendering cadence is measured separately from fixed-step simulation time.
 */
export const FRAME_LIMITS = Object.freeze({
  sampleWindow: 120,
  maxCaptures: 60,
  maxSubSteps: 8,
  maxFrameDelta: 0.1
});

const finite = (value, name) => {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new TypeError(name + " must be finite");
  }
  return value;
};

const clone = value => {
  if (typeof structuredClone === "function") return structuredClone(value);
  return JSON.parse(JSON.stringify(value));
};

function percentile(values, fraction) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.max(0, Math.ceil(sorted.length * fraction) - 1))];
}

export class FrameLab {
  constructor({
    targetFPS = 60,
    fixedStep = 1 / 120,
    maxSubSteps = FRAME_LIMITS.maxSubSteps,
    maxFrameDelta = FRAME_LIMITS.maxFrameDelta,
    sampleWindow = FRAME_LIMITS.sampleWindow,
    maxCaptures = FRAME_LIMITS.maxCaptures,
    maxImageDataUrlLength = 750000
  } = {}) {
    this.setTargetFPS(targetFPS);
    this.fixedStep = finite(fixedStep, "fixedStep");
    if (this.fixedStep <= 0 || this.fixedStep > 1 / 30) throw new RangeError("fixedStep must be in (0, 1/30]");
    this.maxSubSteps = Math.max(1, Math.min(32, Math.floor(finite(maxSubSteps, "maxSubSteps"))));
    this.maxFrameDelta = finite(maxFrameDelta, "maxFrameDelta");
    if (this.maxFrameDelta <= 0 || this.maxFrameDelta > 1) throw new RangeError("maxFrameDelta must be in (0, 1]");
    this.sampleWindow = Math.max(2, Math.min(600, Math.floor(sampleWindow)));
    this.maxCaptures = Math.max(1, Math.min(2000, Math.floor(maxCaptures)));
    this.maxImageDataUrlLength = Math.max(1024, Math.min(2_000_000, Math.floor(maxImageDataUrlLength)));
    this.lastTime = null;
    this.nextRenderAt = null;
    this.accumulator = 0;
    this.frameIndex = 0;
    this.simulationSteps = 0;
    this.droppedSeconds = 0;
    this.missedRenderFrames = 0;
    this.samples = [];
    this.captures = [];
    this.nextCaptureId = 1;
  }

  setTargetFPS(value) {
    finite(value, "targetFPS");
    if (value !== 0 && (value < 1 || value > 240)) throw new RangeError("targetFPS must be 0 (uncapped) or between 1 and 240");
    this.targetFPS = value;
    this.nextRenderAt = null;
    this.lastRenderedAt = null;
  }

  advance(now, stepFn, { paused = false } = {}) {
    finite(now, "now");
    if (typeof stepFn !== "function") throw new TypeError("stepFn must be a function");
    if (this.lastTime === null) {
      this.lastTime = now;
      this.nextRenderAt = now + (this.targetFPS > 0 ? 1000 / this.targetFPS : 0);
      this.lastRenderedAt = now;
      this.frameIndex++;
      return this.metrics(0, 0, true);
    }
    const rawDelta = Math.max(0, (now - this.lastTime) / 1000);
    this.lastTime = now;
    const delta = Math.min(rawDelta, this.maxFrameDelta);
    this.droppedSeconds += Math.max(0, rawDelta - delta);
    let steps = 0;
    if (!paused) {
      this.accumulator += delta;
      while (this.accumulator + 1e-12 >= this.fixedStep && steps < this.maxSubSteps) {
        stepFn(this.fixedStep);
        this.accumulator -= this.fixedStep;
        steps++;
        this.simulationSteps++;
      }
      if (this.accumulator >= this.fixedStep) {
        const retained = this.accumulator % this.fixedStep;
        this.droppedSeconds += this.accumulator - retained;
        this.accumulator = retained;
      }
    }

    let shouldRender = true;
    if (this.targetFPS > 0) {
      const interval = 1000 / this.targetFPS;
      if (this.nextRenderAt === null) this.nextRenderAt = now;
      shouldRender = now + 0.25 >= this.nextRenderAt;
      if (shouldRender) {
        const missed = Math.max(0, Math.floor((now - this.nextRenderAt) / interval));
        this.missedRenderFrames += missed;
        this.nextRenderAt += (missed + 1) * interval;
      }
    }
    if (shouldRender) {
      if (this.lastRenderedAt !== null) {
        const renderedDelta = Math.max(0, (now - this.lastRenderedAt) / 1000);
        if (renderedDelta > 0) {
          this.samples.push(renderedDelta);
          if (this.samples.length > this.sampleWindow) this.samples.shift();
        }
      }
      this.lastRenderedAt = now;
      this.frameIndex++;
    }
    return this.metrics(delta, steps, shouldRender);
  }

  singleStep(stepFn) {
    if (typeof stepFn !== "function") throw new TypeError("stepFn must be a function");
    stepFn(this.fixedStep);
    this.simulationSteps++;
    this.frameIndex++;
    this.accumulator = 0;
    return this.simulationSteps;
  }

  metrics(deltaSeconds = 0, steps = 0, rendered = false) {
    const fps = this.samples.length
      ? this.samples.reduce((sum, value) => sum + value, 0) > 0
        ? this.samples.length / this.samples.reduce((sum, value) => sum + value, 0)
        : 0
      : 0;
    const p99 = percentile(this.samples, 0.99);
    return {
      frameIndex: this.frameIndex,
      fps,
      minFPS: this.samples.length ? 1 / Math.max(...this.samples) : 0,
      onePercentLow: p99 > 0 ? 1 / p99 : 0,
      frameTimeMs: deltaSeconds * 1000,
      simulationSteps: this.simulationSteps,
      stepsThisFrame: steps,
      interpolationAlpha: this.accumulator / this.fixedStep,
      droppedSeconds: this.droppedSeconds,
      missedRenderFrames: this.missedRenderFrames,
      rendered,
      targetFPS: this.targetFPS
    };
  }

  capture(snapshot, { timestamp = null, simTick = null, stateHash = null, label = "", imageDataUrl = null } = {}) {
    if (imageDataUrl !== null && (typeof imageDataUrl !== "string" || !/^data:image\/(png|jpeg);base64,/.test(imageDataUrl) || imageDataUrl.length > this.maxImageDataUrlLength)) {
      throw new RangeError("frame image must be a bounded PNG or JPEG data URL");
    }
    const frame = {
      id: this.nextCaptureId++,
      frameIndex: this.frameIndex,
      timestamp: timestamp === null ? this.lastTime : finite(timestamp, "timestamp"),
      simTick,
      stateHash,
      label: String(label).slice(0, 120),
      imageDataUrl,
      snapshot: clone(snapshot)
    };
    this.captures.push(frame);
    if (this.captures.length > this.maxCaptures) this.captures.shift();
    return clone(frame);
  }

  duplicateCapture(id, { label = "" } = {}) {
    const source = this.captures.find(frame => frame.id === id);
    if (!source) throw new RangeError("unknown frame capture");
    return this.capture(source.snapshot, {
      timestamp: this.lastTime,
      simTick: source.simTick,
      stateHash: source.stateHash,
      imageDataUrl: source.imageDataUrl,
      label: label || (source.label ? source.label + " copy" : "duplicate")
    });
  }

  getCapture(id) {
    const frame = this.captures.find(item => item.id === id);
    return frame ? clone(frame) : null;
  }

  exportCaptures() {
    return JSON.stringify({
      format: "ixpansion-holodeck-frames",
      version: 1,
      exportedAt: new Date().toISOString(),
      captures: this.captures
    }, null, 2);
  }
}
