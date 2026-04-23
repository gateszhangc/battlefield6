const { expect, test } = require("@playwright/test");

test.describe("Battlefield 6 static guide", () => {
  test("renders the landing page and official reference links", async ({ page }) => {
    const errors = [];
    page.on("console", (message) => {
      if (message.type() === "error") {
        errors.push(message.text());
      }
    });

    await page.goto("/");

    await expect(page).toHaveTitle(/Battlefield 6 Guide/);
    await expect(page.getByRole("heading", { name: "Battlefield 6", level: 1 })).toBeVisible();
    await expect(page.getByRole("link", { name: "View on Steam" })).toHaveAttribute(
      "href",
      /store\.steampowered\.com\/app\/2807960/
    );
    await expect(page.getByRole("link", { name: "Official EA Site" })).toHaveAttribute(
      "href",
      /ea\.com\/games\/battlefield\/battlefield-6/
    );
    await expect(page.getByText("Oct 10, 2025")).toBeVisible();
    await expect(page.getByText("Battlefield Studios", { exact: true })).toBeVisible();
    await expect(page.getByText("Electronic Arts", { exact: true })).toBeVisible();
    await expect(page.getByText("2807960", { exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Battlefield 6 PC requirements on Steam" })).toBeVisible();
    expect(errors).toEqual([]);
  });

  test("loads brand assets, health check, and SEO endpoints", async ({ page }) => {
    await page.goto("/");

    for (const asset of [
      "/assets/brand/logo-mark.png",
      "/assets/brand/favicon.png",
      "/assets/brand/apple-touch-icon.png",
      "/assets/brand/social-card.png",
      "/healthz",
      "/site.webmanifest",
      "/robots.txt",
      "/sitemap.xml"
    ]) {
      const response = await page.request.get(asset);
      expect(response.ok(), asset).toBe(true);
    }

    const healthResponse = await page.request.get("/healthz");
    expect(await healthResponse.json()).toEqual({ ok: true });

    const jsonLdEntries = await page
      .locator('script[type="application/ld+json"]')
      .evaluateAll((nodes) => nodes.map((node) => JSON.parse(node.textContent)));
    expect(jsonLdEntries).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ "@type": "VideoGame" }),
        expect.objectContaining({ "@type": "WebSite" }),
        expect.objectContaining({ "@type": "FAQPage" })
      ])
    );
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", "https://battlefield6.lol/");
  });

  test("keeps the layout inside the viewport", async ({ page }) => {
    await page.goto("/");

    const pageOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth
    );
    expect(pageOverflow).toBeLessThanOrEqual(2);

    for (const locator of [
      page.getByRole("heading", { name: "Battlefield 6", level: 1 }),
      page.getByRole("link", { name: "View on Steam" }),
      page.getByRole("link", { name: "Official EA Site" }),
      page.getByText("Oct 10, 2025", { exact: true })
    ]) {
      await expect(locator).toBeInViewport();
    }

    const clippedCriticalElements = await page.evaluate(() => {
      const selectors = ["h1", ".hero-copy", ".button", ".fact-strip dd", "h2", "h3"];
      return selectors.flatMap((selector) =>
        [...document.querySelectorAll(selector)]
          .filter((element) => {
            const rect = element.getBoundingClientRect();
            const style = window.getComputedStyle(element);
            return (
              style.display !== "none" &&
              style.visibility !== "hidden" &&
              rect.width > 0 &&
              (rect.left < -1 || rect.right > document.documentElement.clientWidth + 1)
            );
          })
          .map((element) => ({
            selector,
            text: element.textContent.trim().slice(0, 80),
            left: Math.round(element.getBoundingClientRect().left),
            right: Math.round(element.getBoundingClientRect().right),
            viewport: document.documentElement.clientWidth
          }))
      );
    });

    expect(clippedCriticalElements).toEqual([]);
  });

  test("faq content is accessible", async ({ page }) => {
    await page.goto("/");

    const question = page.getByText("Where can I buy Battlefield 6?");
    await question.click();
    await expect(page.getByText("The official destinations are Steam")).toBeVisible();
  });
});
