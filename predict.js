// Random-forest regression: average of every tree's leaf value.
// scikit-learn compares float32 copies of the inputs, so we do the same.
function predictMpg(model, values) {
  const x = values.map(Math.fround);
  let total = 0;
  for (const tree of model.trees) {
    let node = 0;
    while (tree.f[node] !== -1) {
      node = x[tree.f[node]] <= tree.t[node] ? tree.l[node] : tree.r[node];
    }
    total += tree.t[node];
  }
  return total / model.trees.length;
}

if (typeof module !== "undefined") module.exports = { predictMpg };
