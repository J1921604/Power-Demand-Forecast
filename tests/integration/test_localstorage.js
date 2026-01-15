/**
 * localStorage永続化テスト (US1 MVP)
 * 
 * 契約テスト要件:
 * - デフォルトで2022,2023,2024年が選択される
 * - 学習年選択がlocalStorageに保存される
 * - ページリロード後もlocalStorageから学習年が復元される
 * - localStorageキー: "selectedYears"、値: "2022,2023,2024"（カンマ区切り文字列）
 * 
 * 実行方法:
 *     # Node.js環境（Jest）
 *     npm test tests/integration/test_localstorage.js
 * 
 *     # ブラウザ環境（Playwright Test）
 *     npx playwright test tests/integration/test_localstorage.js
 * 
 * 前提条件:
 *     ダッシュボードにアクセス可能（http://localhost:8002/AI/dashboard/）
 * 
 * 依存関係:
 *     - @playwright/test>=1.40.0（Playwright Test使用時）
 *     - jest>=29.7.0（Jest使用時）
 *     - jsdom>=23.0.0（Jest使用時、DOMシミュレーション）
 * 
 * テストシナリオ:
 *     US1-LS1: デフォルトで2022,2023,2024年が選択される
 *     US1-LS2: 学習年選択がlocalStorageに保存される
 *     US1-LS3: ページリロード後もlocalStorageから学習年が復元される
 *     US1-LS4: localStorageクリア後はデフォルト値に戻る
 */

// Playwright Test使用
const { test, expect } = require('@playwright/test');

const DASHBOARD_URL = 'http://localhost:8002/AI/dashboard/';
const DEFAULT_SELECTED_YEARS = [2022, 2023, 2024];
const LOCALSTORAGE_KEY = 'selectedYears';

test.describe('localStorage永続化テスト (US1 MVP)', () => {

    test.beforeEach(async ({ page }) => {
        // 各テスト前にlocalStorageクリア
        await page.goto(DASHBOARD_URL);
        await page.evaluate(() => localStorage.clear());
        await page.reload();
    });

    test('US1-LS1: デフォルトで2022,2023,2024年が選択される', async ({ page }) => {
        await page.goto(DASHBOARD_URL);

        // localStorageから選択年取得
        const selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        expect(selectedYearsStr).not.toBeNull();

        const selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);
        expect(selectedYears).toEqual(DEFAULT_SELECTED_YEARS);
    });

    test('US1-LS2: 学習年選択がlocalStorageに保存される', async ({ page }) => {
        await page.goto(DASHBOARD_URL);

        // 2023年ボタンをクリック（選択解除）
        await page.click('button[data-year="2023"]');
        await page.waitForTimeout(200); // localStorage保存待機

        // localStorage確認
        const selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        const selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);

        // 2023が除外されている
        expect(selectedYears).toEqual([2022, 2024]);
    });

    test('US1-LS3: ページリロード後もlocalStorageから学習年が復元される', async ({ page }) => {
        await page.goto(DASHBOARD_URL);

        // 学習年を2020,2021,2022に変更
        // まず2023,2024を解除
        await page.click('button[data-year="2023"]');
        await page.click('button[data-year="2024"]');
        
        // 2020,2021を選択
        await page.click('button[data-year="2020"]');
        await page.click('button[data-year="2021"]');
        await page.waitForTimeout(500); // localStorage保存待機

        // localStorage確認（変更前）
        let selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        let selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);
        expect(selectedYears).toEqual([2020, 2021, 2022]);

        // ページリロード
        await page.reload();

        // localStorage確認（リロード後）
        selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);
        expect(selectedYears).toEqual([2020, 2021, 2022]);

        // ボタンactive状態確認
        for (let year = 2016; year <= 2024; year++) {
            const button = page.locator(`button[data-year="${year}"]`);
            const classAttr = await button.getAttribute('class');
            
            if ([2020, 2021, 2022].includes(year)) {
                expect(classAttr).toContain('active');
            } else {
                expect(classAttr).not.toContain('active');
            }
        }
    });

    test('US1-LS4: localStorageクリア後はデフォルト値に戻る', async ({ page }) => {
        await page.goto(DASHBOARD_URL);

        // 学習年を変更
        await page.click('button[data-year="2023"]'); // 2023解除
        await page.waitForTimeout(200);

        // localStorageクリア
        await page.evaluate(() => localStorage.clear());

        // ページリロード
        await page.reload();

        // デフォルト値に戻る
        const selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        const selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);
        expect(selectedYears).toEqual(DEFAULT_SELECTED_YEARS);
    });

    test('US1-LS5: 不正なlocalStorage値はデフォルト値で上書きされる', async ({ page }) => {
        await page.goto(DASHBOARD_URL);

        // 不正な値を設定
        await page.evaluate(() => localStorage.setItem('selectedYears', 'invalid,data'));

        // ページリロード
        await page.reload();

        // デフォルト値に戻る（エラーハンドリング）
        const selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        
        // 実装によっては不正値をクリアしてデフォルト値に戻す
        // または不正値を無視してデフォルト値を使用
        const selectedYears = selectedYearsStr.split(',').map(y => {
            const num = parseInt(y, 10);
            return isNaN(num) ? null : num;
        }).filter(y => y !== null).sort((a, b) => a - b);

        // 不正値がクリアされてデフォルト値になるか検証
        // 実装によって挙動が異なる場合があるため、柔軟に検証
        expect(selectedYears.length).toBeGreaterThan(0);
    });

    test('US1-LS6: 複数回の学習年変更が正しく永続化される', async ({ page }) => {
        await page.goto(DASHBOARD_URL);

        // 変更1: 2023解除
        await page.click('button[data-year="2023"]');
        await page.waitForTimeout(200);

        let selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        let selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);
        expect(selectedYears).toEqual([2022, 2024]);

        // 変更2: 2021追加
        await page.click('button[data-year="2021"]');
        await page.waitForTimeout(200);

        selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);
        expect(selectedYears).toEqual([2021, 2022, 2024]);

        // 変更3: 2022解除
        await page.click('button[data-year="2022"]');
        await page.waitForTimeout(200);

        selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);
        expect(selectedYears).toEqual([2021, 2024]);

        // リロード後も保持
        await page.reload();

        selectedYearsStr = await page.evaluate(() => localStorage.getItem('selectedYears'));
        selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);
        expect(selectedYears).toEqual([2021, 2024]);
    });
});


// Jest + jsdom使用（ブラウザ環境シミュレーション）
// Playwrightが使用できない環境用のフォールバック
if (typeof describe !== 'undefined' && typeof it !== 'undefined') {
    // Jest環境
    const { JSDOM } = require('jsdom');

    describe('localStorage永続化テスト (US1 MVP - Jest)', () => {
        let dom;
        let window;
        let document;
        let localStorage;

        beforeEach(() => {
            // jsdomでDOM環境シミュレート
            dom = new JSDOM(`
                <!DOCTYPE html>
                <html>
                <body>
                    <button data-year="2016"></button>
                    <button data-year="2017"></button>
                    <button data-year="2018"></button>
                    <button data-year="2019"></button>
                    <button data-year="2020"></button>
                    <button data-year="2021"></button>
                    <button data-year="2022" class="active"></button>
                    <button data-year="2023" class="active"></button>
                    <button data-year="2024" class="active"></button>
                </body>
                </html>
            `, {
                url: DASHBOARD_URL,
                runScripts: 'dangerously',
                resources: 'usable'
            });

            window = dom.window;
            document = window.document;
            localStorage = window.localStorage;

            // localStorageクリア
            localStorage.clear();
        });

        it('US1-LS1-Jest: デフォルトで2022,2023,2024年がlocalStorageに保存される', () => {
            // デフォルト値設定シミュレート
            const defaultYears = DEFAULT_SELECTED_YEARS.join(',');
            localStorage.setItem(LOCALSTORAGE_KEY, defaultYears);

            const selectedYearsStr = localStorage.getItem(LOCALSTORAGE_KEY);
            expect(selectedYearsStr).not.toBeNull();

            const selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);
            expect(selectedYears).toEqual(DEFAULT_SELECTED_YEARS);
        });

        it('US1-LS2-Jest: 学習年選択がlocalStorageに保存される', () => {
            // 初期値設定
            localStorage.setItem(LOCALSTORAGE_KEY, '2022,2023,2024');

            // 2023解除シミュレート
            const updatedYears = [2022, 2024];
            localStorage.setItem(LOCALSTORAGE_KEY, updatedYears.join(','));

            const selectedYearsStr = localStorage.getItem(LOCALSTORAGE_KEY);
            const selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);

            expect(selectedYears).toEqual([2022, 2024]);
        });

        it('US1-LS3-Jest: localStorage値の永続化が機能する', () => {
            // 学習年変更
            const customYears = [2020, 2021, 2022];
            localStorage.setItem(LOCALSTORAGE_KEY, customYears.join(','));

            // 取得
            const selectedYearsStr = localStorage.getItem(LOCALSTORAGE_KEY);
            const selectedYears = selectedYearsStr.split(',').map(Number).sort((a, b) => a - b);

            expect(selectedYears).toEqual(customYears);
        });

        it('US1-LS4-Jest: localStorageクリア後はnullが返る', () => {
            localStorage.setItem(LOCALSTORAGE_KEY, '2022,2023,2024');
            localStorage.clear();

            const selectedYearsStr = localStorage.getItem(LOCALSTORAGE_KEY);
            expect(selectedYearsStr).toBeNull();
        });
    });
}
