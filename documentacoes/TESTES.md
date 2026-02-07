# 🧪 Guia de Testes Unitários

Este documento descreve como executar e criar testes unitários para o projeto.

## 📋 Estrutura de Testes

### Backend
- **Framework**: Jest + Supertest
- **Localização**: `backend/__tests__/`
- **Configuração**: `backend/jest.config.js`

### Frontend
- **Framework**: Vitest + React Testing Library
- **Localização**: `frontend/src/__tests__/`
- **Configuração**: `frontend/vitest.config.js`

## 🚀 Como Executar Testes

### Backend

```bash
cd backend
npm install
npm test
```

**Comandos disponíveis:**
- `npm test` - Executar todos os testes
- `npm run test:watch` - Executar testes em modo watch
- `npm run test:coverage` - Executar testes com cobertura

### Frontend

```bash
cd frontend
npm install
npm test
```

**Comandos disponíveis:**
- `npm test` - Executar todos os testes
- `npm run test:ui` - Executar testes com interface gráfica
- `npm run test:coverage` - Executar testes com cobertura

## 📝 Testes Implementados

### Backend

#### `status_calculator.test.js`
- ✅ Cálculo de status para milestones
- ✅ Cálculo de status para atividades concluídas
- ✅ Cálculo de status para atividades em execução
- ✅ Cálculo de status para atividades a iniciar
- ✅ Cores de status para diferentes estados

#### `message_builder.test.js`
- ✅ Cálculo de estatísticas
- ✅ Verificação de sequências concluídas
- ✅ Identificação de atividades atrasadas
- ✅ Formatação de atrasos
- ✅ Formatação de datas e horas
- ✅ Emojis de status

### Frontend

#### `utils/api.test.js`
- ✅ Interceptor de requisições (adicionar token)
- ✅ Interceptor de respostas (tratamento de erros 401)
- ✅ Tratamento de FormData

#### `contexts/AuthContext.test.jsx`
- ✅ Login com sucesso
- ✅ Login com credenciais inválidas
- ✅ Cadastro de novo usuário
- ✅ Logout
- ✅ Verificação de roles

## ✍️ Como Criar Novos Testes

### Backend

1. Crie um arquivo `__tests__/nome-do-modulo.test.js`
2. Importe o módulo a ser testado
3. Use `describe` para agrupar testes relacionados
4. Use `it` ou `test` para cada caso de teste

**Exemplo:**
```javascript
const { minhaFuncao } = require('../meu-modulo');

describe('meu-modulo', () => {
  it('deve fazer algo corretamente', () => {
    const result = minhaFuncao('input');
    expect(result).toBe('expected-output');
  });
});
```

### Frontend

1. Crie um arquivo `src/__tests__/caminho/componente.test.jsx`
2. Importe o componente ou função a ser testado
3. Use `render` ou `renderHook` do React Testing Library
4. Use `expect` para fazer asserções

**Exemplo:**
```javascript
import { render, screen } from '@testing-library/react';
import MeuComponente from '../MeuComponente';

describe('MeuComponente', () => {
  it('deve renderizar corretamente', () => {
    render(<MeuComponente />);
    expect(screen.getByText('Texto esperado')).toBeInTheDocument();
  });
});
```

## 🎯 Boas Práticas

1. **Nomes descritivos**: Use nomes claros que descrevam o que o teste verifica
2. **Um conceito por teste**: Cada teste deve verificar apenas uma coisa
3. **Arrange-Act-Assert**: Organize seus testes em três partes claras
4. **Mock de dependências**: Use mocks para isolar o código sendo testado
5. **Cobertura**: Procure manter cobertura acima de 80% para código crítico

## 🔍 Debugging de Testes

### Backend
```bash
# Executar um teste específico
npm test -- status_calculator.test.js

# Executar com mais detalhes
npm test -- --verbose

# Executar apenas testes que correspondem a um padrão
npm test -- --testNamePattern="deve calcular"
```

### Frontend
```bash
# Executar um teste específico
npm test -- api.test.js

# Executar em modo watch
npm test -- --watch

# Executar com interface gráfica
npm run test:ui
```

## 📊 Cobertura de Código

Para ver a cobertura de código:

**Backend:**
```bash
cd backend
npm run test:coverage
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
```

Os relatórios de cobertura serão gerados em:
- Backend: `backend/coverage/`
- Frontend: `frontend/coverage/`

## 🐛 Troubleshooting

### Erro: "Cannot find module"
- Verifique se todas as dependências estão instaladas: `npm install`
- Verifique se os caminhos de importação estão corretos

### Erro: "localStorage is not defined" (Frontend)
- O arquivo `src/test/setup.js` já configura mocks do localStorage
- Certifique-se de que o `vitest.config.js` está apontando para o arquivo de setup

### Testes lentos
- Use `vi.mock()` para mockar chamadas de API
- Evite testes que dependem de recursos externos
- Use `beforeEach` para limpar estado entre testes

## 📚 Recursos

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
