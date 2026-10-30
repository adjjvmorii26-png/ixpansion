/**
 * Fixed-timestep accumulator with bounded catch-up.
 *
 * currentTime and reset() use the same unit as requestAnimationFrame: ms.
 * Overload policy: cap accepted frame time, run at most maxSubSteps, then
 * discard whole-step backlog while preserving the fractional interpolation
 * remainder. droppedTimeSeconds exposes discarded simulation time.
 */
export class SimulationClock {
  constructor({ targetFps = 60, maxSubSteps = 5, maxFrameTime = 0.25 } = {}) {
    if (!Number.isFinite(targetFps) || targetFps <= 0) {
      throw new RangeError("targetFps must be finite and > 0");
    }
    if (!Number.isSafeInteger(maxSubSteps) || maxSubSteps < 1) {
      throw new RangeError("maxSubSteps must be a positive safe integer");
    }
    if (!Number.isFinite(maxFrameTime) || maxFrameTime <= 0) {
      throw new RangeError("maxFrameTime must be finite and > 0");
    }

    this.timestep = 1 / targetFps;
    this.maxSubSteps = maxSubSteps;
    this.maxFrameTime = maxFrameTime;
    this.accumulator = 0;
    this.lastTime = null;
    this.tickCount = 0;
    this.droppedTimeSeconds = 0;
    this.overloadCount = 0;
  }

  reset(currentTime = null, { resetTicks = false } = {}) {
    if (currentTime !== null && !Number.isFinite(currentTime)) {
      throw new TypeError("currentTime must be finite or null");
    }
    this.accumulator = 0;
    this.lastTime = currentTime;
    this.droppedTimeSeconds = 0;
    this.overloadCount = 0;
    if (resetTicks) this.tickCount = 0;
  }

  tick(currentTime, updateCallback) {
    if (!Number.isFinite(currentTime)) {
      throw new TypeError("currentTime must be finite");
    }
    if (typeof updateCallback !== "function") {
      throw new TypeError("updateCallback must be a function");
    }
    if (this.lastTime === null) {
      this.lastTime = currentTime;
      return 0;
    }
    const elapsed = (currentTime - this.lastTime) / 1000;
    this.lastTime = currentTime;
    if (elapsed < 0) {
      // A clock reset (e.g. test harness or navigation) must not advance time.
      this.accumulator = 0;
      return 0;
    }

    const accepted = Math.min(elapsed, this.maxFrameTime);
    this.droppedTimeSeconds += elapsed - accepted;
    this.accumulator += accepted;

    let steps = 0;
    while (this.accumulator + Number.EPSILON >= this.timestep && steps < this.maxSubSteps) {
      updateCallback(this.timestep, this.tickCount);
      this.tickCount += 1;
      this.accumulator -= this.timestep;
      if (this.accumulator < 0 && this.accumulator > -Number.EPSILON * 8) {
        this.accumulator = 0;
      }
      steps += 1;
    }

    if (this.accumulator >= this.timestep) {
      const wholeStepsDropped = Math.floor(this.accumulator / this.timestep);
      const dropped = wholeStepsDropped * this.timestep;
      this.accumulator -= dropped;
      this.droppedTimeSeconds += dropped;
      this.overloadCount += 1;
    }

    return this.accumulator / this.timestep;
  }
}
