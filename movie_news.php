<?php

declare(strict_types=1);

header('Content-Type: text/html; charset=UTF-8');
mb_internal_encoding('UTF-8');

$tmdb_api_key = 'VLOZ_SVUJ_TMDB_API_KLIC';
$region = 'CZ';
$language = 'cs-CZ';
$cacheTtl = 86400; // 24 hodin
$cacheFile = __DIR__ . '/cache/tmdb_upcoming_' . strtolower($region) . '.json';

function tmdbRequest(string $url): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_FOLLOWLOCATION => true,
    ]);

    $body = curl_exec($ch);
    $error = curl_error($ch);
    $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($body === false) {
        return ['ok' => false, 'error' => 'cURL chyba: ' . $error, 'status' => $status];
    }

    $data = json_decode($body, true);
    if ($status !== 200 || !is_array($data)) {
        return ['ok' => false, 'error' => 'TMDB HTTP ' . $status, 'status' => $status];
    }

    return ['ok' => true, 'data' => $data, 'status' => $status];
}

function getServiceMap(): array
{
    return [
        'Netflix' => ['label' => 'N', 'class' => 'bg-red-600 text-white'],
        'Max' => ['label' => 'HBO', 'class' => 'bg-indigo-600 text-white'],
        'Disney Plus' => ['label' => 'D+', 'class' => 'bg-blue-600 text-white'],
        'Paramount Plus' => ['label' => 'P+', 'class' => 'bg-sky-600 text-white'],
    ];
}

function extractAvailability(array $providersResult): array
{
    $serviceMap = getServiceMap();
    $availability = [];

    $flatrate = $providersResult['flatrate'] ?? [];
    foreach ($flatrate as $provider) {
        $name = $provider['provider_name'] ?? '';
        if (isset($serviceMap[$name])) {
            $availability[$name] = $serviceMap[$name];
        }
    }

    $inTheaters = !empty($providersResult['ads']) && is_array($providersResult['ads']);

    return [
        'services' => array_values($availability),
        'in_theaters' => $inTheaters,
    ];
}

$movies = [];
$errorMessage = null;
$fromCache = false;

if (file_exists($cacheFile) && (time() - filemtime($cacheFile) < $cacheTtl)) {
    $cached = file_get_contents($cacheFile);
    $cachedData = $cached ? json_decode($cached, true) : null;
    if (is_array($cachedData) && isset($cachedData['movies']) && is_array($cachedData['movies'])) {
        $movies = $cachedData['movies'];
        $fromCache = true;
    }
}

if ($movies === []) {
    if ($tmdb_api_key === '' || $tmdb_api_key === 'VLOZ_SVUJ_TMDB_API_KLIC') {
        $errorMessage = 'Chybí TMDB API klíč. Vlož hodnotu do $tmdb_api_key.';
    } else {
        $upcomingUrl = 'https://api.themoviedb.org/3/movie/upcoming?' . http_build_query([
            'api_key' => $tmdb_api_key,
            'language' => $language,
            'region' => $region,
            'page' => 1,
        ]);

        $upcomingResponse = tmdbRequest($upcomingUrl);

        if (!$upcomingResponse['ok']) {
            $errorMessage = 'Nepodařilo se načíst movie/upcoming: ' . $upcomingResponse['error'];
        } else {
            $results = $upcomingResponse['data']['results'] ?? [];
            $results = is_array($results) ? array_slice($results, 0, 20) : [];

            foreach ($results as $movie) {
                if (!is_array($movie)) {
                    continue;
                }

                $movieId = (int) ($movie['id'] ?? 0);
                if ($movieId <= 0) {
                    continue;
                }

                $providersUrl = 'https://api.themoviedb.org/3/movie/' . $movieId . '/watch/providers?' . http_build_query([
                    'api_key' => $tmdb_api_key,
                    'watch_region' => $region,
                ]);

                $providersResponse = tmdbRequest($providersUrl);
                $providersResult = [];
                if ($providersResponse['ok']) {
                    $providersResult = $providersResponse['data']['results'][$region] ?? [];
                }

                $availability = extractAvailability(is_array($providersResult) ? $providersResult : []);

                $movies[] = [
                    'id' => $movieId,
                    'title' => (string) ($movie['title'] ?? 'Bez názvu'),
                    'release_date' => (string) ($movie['release_date'] ?? ''),
                    'poster_path' => (string) ($movie['poster_path'] ?? ''),
                    'overview' => (string) ($movie['overview'] ?? ''),
                    'services' => $availability['services'],
                    'in_theaters' => $availability['in_theaters'],
                ];
            }

            if ($movies !== []) {
                file_put_contents($cacheFile, json_encode([
                    'cached_at' => date('c'),
                    'movies' => $movies,
                ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT));
            }
        }
    }
}
?>
<!doctype html>
<html lang="cs" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Filmové novinky z TMDB</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = { darkMode: 'class' };
    </script>
</head>
<body class="min-h-screen bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
<div class="mx-auto max-w-7xl px-4 py-10">
    <header class="mb-8 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 p-8 text-white shadow-xl">
        <h1 class="text-3xl font-bold md:text-4xl">Filmové novinky & očekávané hity</h1>
        <p class="mt-2 text-indigo-100">TMDB /movie/upcoming • region CZ • jazyk cs-CZ <?= $fromCache ? '• načteno z cache' : '• načteno živě'; ?></p>
    </header>

    <?php if ($errorMessage !== null): ?>
        <div class="mb-6 rounded-xl border border-rose-300 bg-rose-50 px-4 py-3 text-rose-700 dark:border-rose-700 dark:bg-rose-900/30 dark:text-rose-300">
            <?= htmlspecialchars($errorMessage, ENT_QUOTES, 'UTF-8'); ?>
        </div>
    <?php endif; ?>

    <?php if ($movies !== []): ?>
        <section class="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
            <?php foreach ($movies as $movie): ?>
                <article class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900">
                    <?php if ($movie['poster_path'] !== ''): ?>
                        <img src="https://image.tmdb.org/t/p/w500<?= htmlspecialchars($movie['poster_path'], ENT_QUOTES, 'UTF-8'); ?>" alt="<?= htmlspecialchars($movie['title'], ENT_QUOTES, 'UTF-8'); ?>" class="h-80 w-full object-cover">
                    <?php else: ?>
                        <div class="flex h-80 items-center justify-center bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-300">Bez plakátu</div>
                    <?php endif; ?>

                    <div class="p-4">
                        <h2 class="mb-2 text-lg font-semibold leading-tight"><?= htmlspecialchars($movie['title'], ENT_QUOTES, 'UTF-8'); ?></h2>
                        <p class="mb-3 text-xs text-slate-500 dark:text-slate-400">
                            Premiéra CZ: <?= $movie['release_date'] !== '' ? htmlspecialchars((string) date('d.m.Y', strtotime($movie['release_date'])), ENT_QUOTES, 'UTF-8') : 'Neznámé datum'; ?>
                        </p>

                        <div class="mb-3 flex flex-wrap gap-2">
                            <?php foreach ($movie['services'] as $service): ?>
                                <span class="rounded-full px-2.5 py-1 text-xs font-semibold <?= htmlspecialchars($service['class'], ENT_QUOTES, 'UTF-8'); ?>">
                                    <?= htmlspecialchars($service['label'], ENT_QUOTES, 'UTF-8'); ?>
                                </span>
                            <?php endforeach; ?>

                            <?php if ($movie['services'] === [] && $movie['in_theaters']): ?>
                                <span class="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">V kinech</span>
                            <?php endif; ?>

                            <?php if ($movie['services'] === [] && !$movie['in_theaters']): ?>
                                <span class="rounded-full bg-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">Bez dostupnosti</span>
                            <?php endif; ?>
                        </div>

                        <p class="text-sm text-slate-600 dark:text-slate-300">
                            <?= htmlspecialchars(mb_strimwidth($movie['overview'], 0, 200, '...'), ENT_QUOTES, 'UTF-8'); ?>
                        </p>
                    </div>
                </article>
            <?php endforeach; ?>
        </section>
    <?php endif; ?>
</div>
</body>
</html>
