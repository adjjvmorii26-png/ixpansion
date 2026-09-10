const {run:s}=require("../solid_logic/solid_core.js");
const {run:l}=require("../liquid_memory/liquid_flow.js");
const {run:g}=require("../gas_drift/drift_diffusion.js");
const {run:q}=require("../quantum_condensate/condensate_collapse.js");
async function main(){console.log("Manifold Terminal…\n");console.log("Solid:",s(0));console.log("Liquid:",l(0));console.log("Gas:",g(0));console.log("Quantum:",q(0));}
if(require.main===module)main();
