// Ejemplos de Lógica TEO 2.pdf y variantes identificadas en source; páginas del PDF.
const numbers = {
  domain: ['1', '2', '3'], functions: [], predicates: [['P', 1], ['R', 2]],
  function_rows: {}, relations: { P: [['1'], ['2']], R: [['1', '3'], ['2', '1'], ['3', '2']] },
};
const constant = {
  domain: ['a', 'b', 'c'], functions: [['i', 0]], predicates: [['R', 1], ['Q', 2]],
  function_rows: { i: [[[], 'a']] },
  relations: { R: [['b'], ['c']], Q: [['a', 'a'], ['a', 'b'], ['a', 'c'], ['b', 'c'], ['c', 'c']] },
};
const binaryFunction = {
  domain: ['a', 'b', 'c'], functions: [['f', 2]], predicates: [['P', 2]],
  function_rows: { f: [
    [['a', 'a'], 'b'], [['a', 'b'], 'a'], [['a', 'c'], 'c'],
    [['b', 'a'], 'a'], [['b', 'b'], 'b'], [['b', 'c'], 'c'],
    [['c', 'a'], 'c'], [['c', 'b'], 'c'], [['c', 'c'], 'a'],
  ] },
  relations: { P: [['a', 'b'], ['a', 'c'], ['a', 'a']] },
};

export const examples = [
  {
    id: 'pertenencia', title: 'P(x): pertenencia y asignación', source: 'p. 179 · variante abierta de su interpretación',
    description: 'D = {1, 2, 3}. P contiene 1 y 2; R contiene (1, 3), (2, 1) y (3, 2).',
    practice: 'Evalúa con x: 1. Después elige x: 3 y vuelve a evaluar para ver cuándo la tupla deja de pertenecer a P.',
    data: { ...numbers, formula: 'P(x)', assignments: [['x', '1']] },
  },
  {
    id: 'universal', title: '∀x P(x): buscar un contraejemplo', source: 'p. 179 · fórmula e interpretación de las notas',
    description: 'D = {1, 2, 3}. Solo 1 y 2 pertenecen a P. La fórmula pregunta si todos pertenecen a P.',
    practice: 'Evalúa y abre la evidencia. Comprueba por qué 3 es el contraejemplo. Esta fórmula no necesita asignaciones libres.',
    data: { ...numbers, formula: '∀x P(x)', assignments: [] },
  },
  {
    id: 'universal-completo', title: '∀x (P(x) ∨ ¬P(x)): comprobación completa', source: 'p. 179 · variante sobre su interpretación',
    description: 'D = {1, 2, 3}. La fórmula comprueba, para cada elemento, la disyunción entre pertenecer a P y no pertenecer a P.',
    practice: 'Evalúa y abre las tres comprobaciones de x. Para justificar este universal verdadero debe recorrerse todo D; un solo caso no basta.',
    data: { ...numbers, formula: '∀x (P(x) ∨ ¬P(x))', assignments: [] },
  },
  {
    id: 'relaciones', title: '∀x ∃y R(x,y): cuantificadores anidados', source: 'p. 179 · fórmula e interpretación de las notas',
    description: 'R contiene (1, 3), (2, 1) y (3, 2). Cada elemento del dominio aparece como primera componente de alguna pareja.',
    practice: 'Abre cada comprobación de x para encontrar su testigo y. No hace falta que el mismo y sirva para todos los x.',
    data: { ...numbers, formula: '∀x ∃y R(x,y)', assignments: [] },
  },
  {
    id: 'testigo', title: '∃x P(x): encontrar un testigo', source: 'p. 179 · variante sobre su interpretación',
    description: 'D = {1, 2, 3} y P contiene 1 y 2. Basta encontrar un elemento que pertenezca a P.',
    practice: 'Evalúa. En Comparar un cambio, quita (1) de P: la verdad se mantiene, pero el testigo pasa a ser 2.',
    data: { ...numbers, formula: '∃x P(x)', assignments: [] },
  },
  {
    id: 'contradiccion', title: '∃x (P(x) ∧ ¬P(x)): revisar todo D', source: 'p. 179 · variante sobre su interpretación',
    description: 'Usa la misma interpretación de P. La fórmula pide un elemento que pertenezca y no pertenezca a P a la vez.',
    practice: 'Abre la evidencia para ver que se comprueban los tres elementos sin encontrar un testigo.',
    data: { ...numbers, formula: '∃x (P(x) ∧ ¬P(x))', assignments: [] },
  },
  {
    id: 'constante', title: '¬R(i): interpretar una constante', source: 'p. 181 · fórmula e interpretación de las notas',
    description: 'D = {a, b, c}. La constante i se interpreta como a y R contiene b y c. La ficha de i permite elegir el elemento del dominio que designa.',
    practice: 'Evalúa. Después compara la salida de i: cambia a por b y observa cómo cambia la verdad de ¬R(i).',
    data: { ...constant, formula: '¬R(i)', assignments: [] },
  },
  {
    id: 'constante-relacion', title: '∃y Q(i,y): constante y relación binaria', source: 'p. 181 · fórmula e interpretación de las notas',
    description: 'i se interpreta como a. Q contiene (a, a), (a, b), (a, c), (b, c) y (c, c).',
    practice: 'Evalúa y abre la evidencia para ver la consulta de i y el testigo que completa la pareja Q(i,y).',
    data: { ...constant, formula: '∃y Q(i,y)', assignments: [] },
  },
  {
    id: 'funcion', title: 'P(x, f(x,y)): evaluar términos', source: 'p. 187 · ejemplo manuscrito de las notas',
    description: 'D = {a, b, c}. P contiene (a, b), (a, c) y (a, a). La tabla de f define sus nueve salidas; puedes consultarla y editarla en la ficha de f.',
    practice: 'Con x: b, y: b, f(b,b) produce b y (b,b) no pertenece a P. Cambia x: a para obtener una tupla que sí pertenece.',
    data: { ...binaryFunction, formula: 'P(x, f(x,y))', assignments: [['x', 'b'], ['y', 'b']] },
  },
  {
    id: 'integrado', title: 'Caso integrado: cuantificadores, función y constante', source: 'combinación didáctica de las interpretaciones de las pp. 181 y 187',
    description: 'En D = {a, b, c}, i designa a, R contiene b y c, y Q contiene (a,a), (a,b), (a,c), (b,c) y (c,c). Se utiliza la tabla completa de la función binaria f del ejemplo de términos.',
    practice: 'Localiza el contraejemplo x: c y revisa los tres valores de y. Después, en Comparar un cambio, abre Elegir otro dato manualmente y cambia solo el valor de f(c, c) de a a b. Compara las dos evidencias.',
    data: {
      ...constant, functions: [['i', 0], ['f', 2]],
      function_rows: { ...constant.function_rows, ...binaryFunction.function_rows },
      formula: '(∀x ∃y (Q(x,y) ∧ R(f(x,y)))) ∧ ¬R(i)', assignments: [],
    },
  },
  {
    id: 'socrates', title: 'Sócrates: hombres y mortales', source: 'pp. 108–115 · adaptación a un dominio finito',
    description: 'H significa «es hombre» y M, «es mortal»; s nombra a Sócrates. Para probarlo aquí se añade D = {Sócrates, Platón}, ambos en H y M.',
    practice: 'Evalúa. Compara la pertenencia de Platón a M: quítala para comprobar que ya no todos los hombres del dominio son mortales.',
    data: {
      domain: ['Sócrates', 'Platón'], functions: [['s', 0]], predicates: [['H', 1], ['M', 1]],
      function_rows: { s: [[[], 'Sócrates']] },
      relations: { H: [['Sócrates'], ['Platón']], M: [['Sócrates'], ['Platón']] },
      formula: '(∀x (H(x) → M(x))) ∧ H(s)', assignments: [],
    },
  },
];
