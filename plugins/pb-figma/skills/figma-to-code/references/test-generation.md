# Test Generation Reference

Bu dokuman, Figma-to-code donusumunde Phase 5 Handoff asamasinda otomatik test uretimi icin kullanilir.

---

## Test Generation Workflow

```
                    +-----------------------+
                    |    Component Code     |
                    |    (React + Props)    |
                    +-----------+-----------+
                                |
                                v
                    +-----------+-----------+
                    |   Analyze Component   |
                    |   - Props & Types     |
                    |   - Variants          |
                    |   - Event Handlers    |
                    +-----------+-----------+
                                |
            +-------------------+-------------------+
            |                   |                   |
            v                   v                   v
    +-------+-------+   +-------+-------+   +-------+-------+
    |   Unit Tests  |   |  Integration  |   | Visual Tests  |
    |   (Vitest)    |   |  (RTL + A11y) |   |  (Playwright) |
    +---------------+   +---------------+   +---------------+
            |                   |                   |
            v                   v                   v
    ComponentName.test.tsx   (included)   ComponentName.visual.spec.ts
```

---

## Phase 5 Test Generation Checklist

Phase 5 Handoff sirasinda asagidaki test dosyalari uretilmelidir:

| Dosya | Zorunluluk | Aciklama |
|-------|------------|----------|
| `{ComponentName}.test.tsx` | **ZORUNLU** | Unit + Integration testleri |
| `jest-axe` accessibility | **ZORUNLU** | `toHaveNoViolations` assertion |
| Snapshot test | Opsiyonel | Variant bazli snapshot |
| `{ComponentName}.visual.spec.ts` | Opsiyonel* | Playwright visual regression |

> *Visual test dosyasi, projede Playwright kurulu ise uretilir.

### Minimum Test Gereksinimleri

Her component icin en az:
- [ ] 1 render testi (crashes olmadan render)
- [ ] 1 props testi (variant veya className)
- [ ] 1 accessibility testi (jest-axe)
- [ ] 1 interaction testi (event handler varsa)

---

## Unit Test Template

Asagidaki template, Testing Library ve jest-axe kullanan bir unit test dosyasi uretir.

### Dosya: `{ComponentName}.test.tsx`

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ComponentName } from './ComponentName';

expect.extend(toHaveNoViolations);

describe('ComponentName', () => {
  // ==========================================
  // RENDERING TESTS
  // ==========================================

  describe('Rendering', () => {
    it('renders without crashing', () => {
      render(<ComponentName />);
      expect(screen.getByTestId('component-name')).toBeInTheDocument();
    });

    it('renders with default props', () => {
      render(<ComponentName />);
      const element = screen.getByTestId('component-name');
      expect(element).toBeVisible();
    });

    it('renders children correctly', () => {
      render(
        <ComponentName>
          <span data-testid="child">Child content</span>
        </ComponentName>
      );
      expect(screen.getByTestId('child')).toBeInTheDocument();
    });
  });

  // ==========================================
  // PROPS TESTS
  // ==========================================

  describe('Props', () => {
    describe('variant prop', () => {
      it('renders default variant correctly', () => {
        render(<ComponentName variant="default" />);
        expect(screen.getByTestId('component-name')).toHaveClass('bg-white');
      });

      it('renders primary variant correctly', () => {
        render(<ComponentName variant="primary" />);
        expect(screen.getByTestId('component-name')).toHaveClass('bg-blue-500');
      });

      it('renders secondary variant correctly', () => {
        render(<ComponentName variant="secondary" />);
        expect(screen.getByTestId('component-name')).toHaveClass('bg-gray-100');
      });
    });

    describe('size prop', () => {
      it('renders sm size correctly', () => {
        render(<ComponentName size="sm" />);
        expect(screen.getByTestId('component-name')).toHaveClass('p-2 text-sm');
      });

      it('renders md size correctly', () => {
        render(<ComponentName size="md" />);
        expect(screen.getByTestId('component-name')).toHaveClass('p-4 text-base');
      });

      it('renders lg size correctly', () => {
        render(<ComponentName size="lg" />);
        expect(screen.getByTestId('component-name')).toHaveClass('p-6 text-lg');
      });
    });

    it('applies custom className', () => {
      render(<ComponentName className="custom-class" />);
      expect(screen.getByTestId('component-name')).toHaveClass('custom-class');
    });
  });

  // ==========================================
  // INTERACTION TESTS
  // ==========================================

  describe('Interactions', () => {
    it('calls onClick when clicked', async () => {
      const handleClick = vi.fn();
      render(<ComponentName onClick={handleClick} />);

      await userEvent.click(screen.getByTestId('component-name'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', async () => {
      const handleClick = vi.fn();
      render(<ComponentName onClick={handleClick} disabled />);

      await userEvent.click(screen.getByTestId('component-name'));
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('is keyboard accessible', async () => {
      render(<ComponentName />);
      const element = screen.getByTestId('component-name');

      await userEvent.tab();
      expect(element).toHaveFocus();
    });

    it('responds to Enter key', async () => {
      const handleClick = vi.fn();
      render(<ComponentName onClick={handleClick} />);
      const element = screen.getByTestId('component-name');

      element.focus();
      await userEvent.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  // ==========================================
  // ACCESSIBILITY TESTS
  // ==========================================

  describe('Accessibility', () => {
    it('has no accessibility violations', async () => {
      const { container } = render(<ComponentName />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has no violations with all variants', async () => {
      const { container: c1 } = render(<ComponentName variant="primary" />);
      const { container: c2 } = render(<ComponentName variant="secondary" />);

      expect(await axe(c1)).toHaveNoViolations();
      expect(await axe(c2)).toHaveNoViolations();
    });

    it('has correct ARIA attributes', () => {
      render(<ComponentName aria-label="Component label" />);
      const element = screen.getByTestId('component-name');
      expect(element).toHaveAttribute('aria-label', 'Component label');
    });

    it('is properly disabled for screen readers', () => {
      render(<ComponentName disabled />);
      expect(screen.getByTestId('component-name')).toHaveAttribute('aria-disabled', 'true');
    });
  });

  // ==========================================
  // SNAPSHOT TESTS
  // ==========================================

  describe('Snapshots', () => {
    it('matches default snapshot', () => {
      const { container } = render(<ComponentName />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('matches primary variant snapshot', () => {
      const { container } = render(<ComponentName variant="primary" />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('matches disabled state snapshot', () => {
      const { container } = render(<ComponentName disabled />);
      expect(container.firstChild).toMatchSnapshot();
    });
  });
});
```

---

## Visual Test Template (Playwright)

Playwright ile visual regression testleri icin kullanilir.

### Dosya: `{ComponentName}.visual.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('ComponentName Visual Tests', () => {
  const componentUrl = '/storybook-preview?component=ComponentName';

  test.beforeEach(async ({ page }) => {
    await page.goto(componentUrl);
    await page.waitForSelector('[data-testid="component-name"]');
  });

  // ==========================================
  // DEFAULT STATE
  // ==========================================

  test('default state screenshot', async ({ page }) => {
    const component = page.locator('[data-testid="component-name"]');

    await expect(component).toHaveScreenshot('component-name-default.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  });

  // ==========================================
  // VIEWPORT TESTS
  // ==========================================

  test('mobile viewport screenshot', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    const component = page.locator('[data-testid="component-name"]');

    await expect(component).toHaveScreenshot('component-name-mobile.png', {
      maxDiffPixels: 100,
    });
  });

  test('tablet viewport screenshot', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    const component = page.locator('[data-testid="component-name"]');

    await expect(component).toHaveScreenshot('component-name-tablet.png', {
      maxDiffPixels: 100,
    });
  });

  // ==========================================
  // INTERACTIVE STATES
  // ==========================================

  test('hover state screenshot', async ({ page }) => {
    const component = page.locator('[data-testid="component-name"]');
    await component.hover();

    // Wait for hover transition
    await page.waitForTimeout(300);

    await expect(component).toHaveScreenshot('component-name-hover.png', {
      maxDiffPixels: 50,
    });
  });

  test('focus state screenshot', async ({ page }) => {
    const focusable = page.locator('[data-testid="component-name"]');
    await focusable.focus();

    await expect(focusable).toHaveScreenshot('component-name-focus.png', {
      maxDiffPixels: 50,
    });
  });

  test('disabled state screenshot', async ({ page }) => {
    await page.goto(`${componentUrl}&disabled=true`);
    const component = page.locator('[data-testid="component-name"]');

    await expect(component).toHaveScreenshot('component-name-disabled.png', {
      maxDiffPixels: 50,
    });
  });

  // ==========================================
  // VARIANT TESTS
  // ==========================================

  test('primary variant screenshot', async ({ page }) => {
    await page.goto(`${componentUrl}&variant=primary`);
    const component = page.locator('[data-testid="component-name"]');

    await expect(component).toHaveScreenshot('component-name-primary.png', {
      maxDiffPixels: 100,
    });
  });

  test('secondary variant screenshot', async ({ page }) => {
    await page.goto(`${componentUrl}&variant=secondary`);
    const component = page.locator('[data-testid="component-name"]');

    await expect(component).toHaveScreenshot('component-name-secondary.png', {
      maxDiffPixels: 100,
    });
  });
});
```

---

## Test Generation Rules

Component analizine gore hangi testlerin uretilecegini belirleyen kurallar:

### Props Analizi

| Prop Tipi | Uretilecek Test |
|-----------|-----------------|
| `variant: 'a' \| 'b' \| 'c'` | Her variant icin ayri test |
| `size: 'sm' \| 'md' \| 'lg'` | Her size icin ayri test |
| `disabled: boolean` | `true` ve `false` icin test |
| `isLoading: boolean` | `true` ve `false` icin test |
| `onClick: () => void` | Click handler testi + disabled kontrolu |
| `onChange: (value) => void` | Change handler testi |
| `className?: string` | Custom className testi |
| `children: ReactNode` | Children rendering testi |

### Event Handler Analizi

```typescript
// Eger component'te bu handler varsa:
interface Props {
  onClick?: () => void;
  onHover?: () => void;
  onFocus?: () => void;
}

// Bu testler uretilir:
// - onClick: click eventi, disabled durumda click
// - onHover: hover eventi
// - onFocus: focus eventi, keyboard navigation
```

### ARIA Attribute Analizi

```typescript
// Eger component'te bu attribute'lar varsa:
<div
  role="button"
  aria-label={label}
  aria-disabled={disabled}
  aria-expanded={isOpen}
/>

// Bu testler uretilir:
// - role attribute kontrolu
// - aria-label kontrolu
// - aria-disabled disabled state'te kontrolu
// - aria-expanded toggle kontrolu
```

### Zorunlu Testler (Her Component Icin)

1. **Render testi** - Component hatasiz render oluyor mu
2. **Default props testi** - Varsayilan degerlerle calisma
3. **className testi** - Custom class uygulanabiliyor mu
4. **Accessibility testi** - jest-axe toHaveNoViolations

### Opsiyonel Testler

| Kosul | Uretilecek Test |
|-------|-----------------|
| Variant prop varsa | Her variant icin ayri test |
| Event handler varsa | Handler cagri testi |
| Interactive element ise | Keyboard accessibility testi |
| Playwright kurulu ise | Visual regression testleri |
| Responsive tasarim ise | Viewport testleri |

---

## Integration with Phase 5

Phase 5 Handoff sirasinda test uretimi icin adimlar:

```
Step 1: Read Component
    |
    +-- ComponentName.tsx dosyasini oku
    +-- Props interface'ini cikart
    +-- Event handler'lari belirle
    |
    v
Step 2: Extract Props
    |
    +-- TypeScript type'larini parse et
    +-- Variant/union type'lari belirle
    +-- Boolean prop'lari belirle
    +-- Handler prop'lari belirle
    |
    v
Step 3: Generate Unit Test
    |
    +-- Template'i kullan
    +-- Props'a gore test case'leri ekle
    +-- Handler varsa interaction testleri ekle
    +-- Accessibility testlerini ekle
    |
    v
Step 4: Generate Visual Test (Opsiyonel)
    |
    +-- Playwright kurulu mu kontrol et
    +-- Storybook preview URL'i belirle
    +-- Viewport testlerini ekle
    +-- State testlerini ekle
    |
    v
Step 5: Run Tests
    |
    +-- npm run test -- ComponentName
    +-- Hata varsa duzelt
    +-- Coverage kontrol et
    |
    v
Step 6: Add to Checklist
    |
    +-- Handoff raporuna test durumunu ekle
    +-- Coverage yuzdesini raporla
    +-- Basarisiz testleri listele
```

### Handoff Raporuna Test Ekleme

```markdown
### 🧪 Test Status

| Test Type | File | Status | Coverage |
|-----------|------|--------|----------|
| Unit | `ComponentName.test.tsx` | ✅ 12/12 passed | 94% |
| A11y | (included in unit) | ✅ No violations | - |
| Visual | `ComponentName.visual.spec.ts` | ✅ 6/6 passed | - |

**Coverage Summary:**
- Statements: 94%
- Branches: 88%
- Functions: 100%
- Lines: 93%
```

---

## Test File Naming

| Component | Unit Test | Visual Test |
|-----------|-----------|-------------|
| `Button.tsx` | `Button.test.tsx` | `Button.visual.spec.ts` |
| `HeroCard.tsx` | `HeroCard.test.tsx` | `HeroCard.visual.spec.ts` |
| `NavigationMenu.tsx` | `NavigationMenu.test.tsx` | `NavigationMenu.visual.spec.ts` |
| `PricingTable.tsx` | `PricingTable.test.tsx` | `PricingTable.visual.spec.ts` |
| `UserAvatar.tsx` | `UserAvatar.test.tsx` | `UserAvatar.visual.spec.ts` |

### Dosya Konumu

```
src/
└── components/
    └── ComponentName/
        ├── ComponentName.tsx           # Component
        ├── ComponentName.test.tsx      # Unit tests (ayni dizin)
        └── ComponentName.stories.tsx   # Storybook

tests/
└── visual/
    └── ComponentName.visual.spec.ts    # Visual tests (ayri dizin)
```

---

## Running Tests

### Temel Komutlar

```bash
# Tum unit testleri calistir
npm run test

# Belirli component'i test et
npm run test -- ComponentName

# Watch modunda calistir (gelistirme sirasinda)
npm run test:watch

# Coverage raporu ile calistir
npm run test:coverage

# Sadece accessibility testlerini calistir
npm run test -- --grep "accessibility"
```

### Visual Test Komutlari

```bash
# Tum visual testleri calistir
npm run test:visual

# Snapshot'lari guncelle (yeni baseline)
npm run test:visual:update

# Belirli component icin visual test
npx playwright test ComponentName.visual.spec.ts

# UI modunda calistir (debug icin)
npx playwright test --ui
```

### CI/CD Komutlari

```bash
# Tum testleri coverage ile calistir (CI)
npm run test:coverage -- --run

# Visual testleri CI'da calistir
npm run test:visual -- --reporter=json

# Tum test suite'i calistir
npm run test:all
```

---

## Coverage Requirements

### Minimum Thresholds

| Metrik | Minimum | Hedef | Aciklama |
|--------|---------|-------|----------|
| Statements | 80% | 90% | Tum kod satirlari |
| Branches | 80% | 85% | if/else, ternary |
| Functions | 80% | 90% | Tum fonksiyonlar |
| Lines | 80% | 90% | Calistirilan satirlar |

### Coverage Kontrolu

```bash
# Coverage raporu olustur
npm run test:coverage

# HTML raporu ac
open coverage/index.html
```

### Coverage Raporlama

Test uretimi sirasinda coverage sonuclari toplanir ve handoff raporuna eklenir:

```typescript
// Test runner output parsing
interface CoverageResult {
  statements: number;  // 94
  branches: number;    // 88
  functions: number;   // 100
  lines: number;       // 93
  passedTests: number; // 12
  totalTests: number;  // 12
}
```

### Minimum Gereksinim Kontrolu

```typescript
function checkCoverageThresholds(coverage: CoverageResult): boolean {
  const THRESHOLDS = {
    statements: 80,
    branches: 80,
    functions: 80,
    lines: 80,
  };

  return (
    coverage.statements >= THRESHOLDS.statements &&
    coverage.branches >= THRESHOLDS.branches &&
    coverage.functions >= THRESHOLDS.functions &&
    coverage.lines >= THRESHOLDS.lines
  );
}
```

---

## Quick Reference

### Test Dosyasi Olusturma Adimlari

1. Component dosyasini oku
2. Props interface'ini cikart
3. Unit test template'ini uygula
4. Props'a gore test case'leri ekle
5. Visual test'i (opsiyonel) olustur
6. Testleri calistir ve dogrula
7. Coverage'i kontrol et
8. Handoff raporuna ekle

### Gerekli Dependencies

```json
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/user-event": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "jest-axe": "^8.0.0",
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

### CI Integration

```yaml
# .github/workflows/test.yml
- name: Run Unit Tests
  run: npm run test:coverage -- --run

- name: Run Visual Tests
  run: npm run test:visual

- name: Upload Coverage
  uses: codecov/codecov-action@v3
```
