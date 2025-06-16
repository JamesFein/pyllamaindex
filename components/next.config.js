/** @type {import('next').NextConfig} */
const nextConfig = {
  // 配置API代理到FastAPI后端
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
  // 允许跨域
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          { key: "Access-Control-Allow-Credentials", value: "true" },
          { key: "Access-Control-Allow-Origin", value: "*" },
          {
            key: "Access-Control-Allow-Methods",
            value: "GET,OPTIONS,PATCH,DELETE,POST,PUT",
          },
          {
            key: "Access-Control-Allow-Headers",
            value:
              "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version",
          },
        ],
      },
    ];
  },
  // 输出配置
  output: "standalone",
  // 启用严格模式，但通过其他方式处理渲染问题
  reactStrictMode: true,
  // 添加实验性功能配置
  experimental: {
    // 禁用一些可能导致问题的实验性功能
    optimizePackageImports: ["@llamaindex/chat-ui", "ai"],
  },
};

module.exports = nextConfig;
