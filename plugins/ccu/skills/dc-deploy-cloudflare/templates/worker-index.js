// Generate one ROUTES entry per artboard that is a page.
// Shared components pulled in via <dc-import> are NOT routes — the asset layer
// serves them directly by filename.
const ROUTES = {
  "/": "home",
  // "/about": "about",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Trailing slash breaks relative asset paths while still returning 200.
    // Redirect instead of serving.
    if (url.pathname !== "/" && url.pathname.endsWith("/")) {
      const canonical = new URL(url);
      canonical.pathname = url.pathname.replace(/\/+$/, "");
      if (ROUTES[canonical.pathname]) {
        return Response.redirect(canonical.toString(), 301);
      }
    }

    const page = ROUTES[url.pathname];
    if (page) {
      const target = new URL(request.url);
      target.pathname = `/${page}.dc.html`;
      return env.ASSETS.fetch(new Request(target, request));
    }

    return new Response("404", {
      status: 404,
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  },
};
