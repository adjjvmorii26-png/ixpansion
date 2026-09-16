// Organism Dashboard - Live State Visualization
class OrganismDashboard {
  constructor(options = {}) {
    this.coherence = options.coherence || 0.5;
    this.entropy = options.entropy || 0.5;
    this.modules = options.modules || 0;
    this.wave = options.wave || 0;
    this.init();
  }
  
  init() {
    this.render();
    this.setupAnimations();
    this.startPulse();
  }
  
  render() {
    const container = document.getElementById('organism-state');
    if (!container) return;
    
    const coherenceColor = `hsl(210, ${this.coherence * 90}%, 25%)`;
    const entropyColor = `hsl(40, ${this.entropy * 90}%, 30%)`;
    
    container.innerHTML = `
      <div class="coherence-bar">
        <div class="fill" style="width: ${this.coherence * 100}%"></div>
      </div>
      <div class="entropy-bar">
        <div class="fill" style="width: ${this.entropy * 100}%"></div>
      </div>
      <div class="module-count">Modules: ${this.modules}</div>
      <div class="wave-indicator">Wave: ${this.wave}</div>
    `;
  }
  
  setupAnimations() {
    const bars = document.querySelectorAll('.bar-fill');
    bars.forEach(bar => {
      bar.style.transition = 'width 1s ease-out';
    });
  }
  
  startPulse() {
    setInterval(() => {
      this.coherence += Math.random() * 0.05 - 0.025;
      this.entropy -= Math.random() * 0.05 - 0.025;
      this.coherence = Math.max(0, Math.min(1, this.coherence));
      this.entropy = Math.max(0, Math.min(1, this.entropy));
      this.render();
    }, 500);
  }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  new OrganismDashboard({
    coherence: 0.85,
    entropy: 0.15,
    modules: 1088,
    wave: 733
  });
});
