export const buildPrompt = ({
  contexto,
  ciclo,
  modulo,
  nivel,
  includeSolution
}) => {
  return `
Eres un profesor experto en Formación Profesional.

Contexto oficial:
${contexto}

Genera una actividad para:
- Ciclo: ${ciclo}
- Módulo: ${modulo}
- Nivel: ${nivel}

${includeSolution ? "Incluye solución detallada." : "NO incluyas la solución."}
`;
};
