<?php

declare(strict_types=1);

/**
 * Cron skript pro stažení blížících se release dat z TMDB a uložení do DB.
 *
 * Spuštění (příklad):
 * php /path/to/project/cron/fetch_data.php
 *
 * Nutné ENV proměnné:
 * - TMDB_API_KEY
 * Volitelné:
 * - TMDB_REGION (default CZ)
 * - DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
 */

require __DIR__ . '/../includes/db.php';

if (!$pdo instanceof PDO) {
    fwrite(STDERR, "DB connection failed.\n");
    exit(1);
}

$apiKey = getenv('TMDB_API_KEY') ?: '';
$region = getenv('TMDB_REGION') ?: 'CZ';

if ($apiKey === '') {
    fwrite(STDERR, "Missing TMDB_API_KEY environment variable.\n");
    exit(1);
}

$today = new DateTimeImmutable('today');
$windowEnd = $today->modify('+60 days');

$query = http_build_query([
    'api_key' => $apiKey,
    'language' => 'cs-CZ',
    'region' => $region,
    'release_date.gte' => $today->format('Y-m-d'),
    'release_date.lte' => $windowEnd->format('Y-m-d'),
    'sort_by' => 'release_date.asc',
    'page' => 1,
]);

$url = 'https://api.themoviedb.org/3/discover/movie?' . $query;
$payload = @file_get_contents($url);

if ($payload === false) {
    fwrite(STDERR, "Failed to fetch data from TMDB.\n");
    exit(1);
}

$data = json_decode($payload, true);
if (!is_array($data) || !isset($data['results']) || !is_array($data['results'])) {
    fwrite(STDERR, "Invalid TMDB response format.\n");
    exit(1);
}

$insertSql = '
    INSERT INTO releases (title, platform, release_date, note, source, external_id)
    VALUES (:title, :platform, :release_date, :note, :source, :external_id)
    ON DUPLICATE KEY UPDATE
        title = VALUES(title),
        platform = VALUES(platform),
        release_date = VALUES(release_date),
        note = VALUES(note)
';

$statement = $pdo->prepare($insertSql);
$savedCount = 0;

foreach ($data['results'] as $item) {
    if (!is_array($item)) {
        continue;
    }

    $title = trim((string) ($item['title'] ?? ''));
    $releaseDate = (string) ($item['release_date'] ?? '');
    $externalId = isset($item['id']) ? (string) $item['id'] : '';

    if ($title === '' || $releaseDate === '' || $externalId === '') {
        continue;
    }

    $note = (string) ($item['overview'] ?? '');
    $note = mb_substr(trim($note), 0, 500);

    $statement->execute([
        'title' => $title,
        'platform' => 'Film',
        'release_date' => $releaseDate,
        'note' => $note,
        'source' => 'tmdb',
        'external_id' => $externalId,
    ]);

    $savedCount++;
}

fwrite(STDOUT, sprintf("Saved/updated %d releases from TMDB.\n", $savedCount));
