export function calculateAgeAtDeath(birthDate, deathDate) {
  if (!birthDate || !deathDate || deathDate < birthDate) return "";
  const [birthYear, birthMonth, birthDay] = birthDate.split("-").map(Number);
  const [deathYear, deathMonth, deathDay] = deathDate.split("-").map(Number);
  return deathYear - birthYear - (deathMonth < birthMonth || (deathMonth === birthMonth && deathDay < birthDay) ? 1 : 0);
}
