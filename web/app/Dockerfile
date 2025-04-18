FROM node:jod-alpine3.20 AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

COPY . /app

# Stage 1: Install dependencies
FROM base AS deps

RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

# Stage 2: Build the app
FROM base AS builder

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN pnpm build


# Stage 3: Run the app
FROM base AS runner

ENV NODE_ENV production

COPY --from=builder /app/.output ./.output

EXPOSE 3000

ENV PORT 3000

CMD node .output/server/index.mjs
