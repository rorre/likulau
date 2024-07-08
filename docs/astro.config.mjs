import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
  integrations: [
    starlight({
      title: "Likulau",
      social: {
        github: "https://github.com/rorre/likulau",
      },
      sidebar: [
        { slug: "introduction" },
        {
          label: "Guides",
          autogenerate: { directory: "guides" },
        },
      ],
    }),
  ],
});
