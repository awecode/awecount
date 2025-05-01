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


# Stage 3: Distribute
FROM base AS dist
RUN mkdir -p /srv
COPY --from=builder /app/dist/spa /srv
