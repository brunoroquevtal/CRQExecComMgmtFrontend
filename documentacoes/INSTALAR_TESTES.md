# 📦 Instalação de Dependências de Testes

## Backend

```bash
cd backend
npm install
```

Isso instalará:
- `jest` - Framework de testes
- `supertest` - Testes de API HTTP

## Frontend

```bash
cd frontend
npm install
```

Isso instalará:
- `vitest` - Framework de testes (compatível com Vite)
- `@testing-library/react` - Utilitários para testar componentes React
- `@testing-library/jest-dom` - Matchers adicionais para DOM
- `@testing-library/user-event` - Simulação de eventos do usuário
- `jsdom` - Ambiente DOM para testes

## Executar Testes

### Backend
```bash
cd backend
npm test
```

### Frontend
```bash
cd frontend
npm test
```

## Próximos Passos

Após instalar as dependências, você pode:
1. Executar os testes: `npm test`
2. Ver cobertura: `npm run test:coverage`
3. Executar em modo watch: `npm run test:watch` (backend) ou `npm test -- --watch` (frontend)

Para mais informações, consulte `TESTES.md`.
