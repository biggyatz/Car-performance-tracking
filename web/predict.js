// Used-car value model exported by train_car_model.py. Mirrors design() in Python.
function carFeatures(model, x) {
  const age = Math.min(35, Math.max(0, model.now - x.year));
  const f = { age, age2: age * age / 10, ev: x.ev ? 1 : 0, ev_age: (x.ev ? 1 : 0) * age };
  const km = x.km == null ? null : Math.min(300000, Math.max(1000, x.km));
  f.km_missing = km == null ? 1 : 0;
  f.log_km = km == null ? 0 : Math.log(km) - Math.log(60000);
  f["m=" + x.make] = 1;
  f["f=" + x.make + " " + x.family] = 1;
  return f;
}
function predictCar(model, x) {
  let z = model.intercept;
  for (const [k, v] of Object.entries(carFeatures(model, x))) if (k in model.coef) z += model.coef[k] * v;
  const q = model.resid_q;
  return { price: Math.exp(z), low: Math.exp(z + q["0.1"]), high: Math.exp(z + q["0.9"]), q1: Math.exp(z + q["0.25"]), q3: Math.exp(z + q["0.75"]) };
}
if (typeof module !== "undefined") module.exports = { predictCar, carFeatures };
