<?php

declare(strict_types=1);

set_time_limit(300);
mb_internal_encoding('UTF-8');

if (PHP_SAPI !== 'cli') {
    header('Content-Type: text/plain; charset=UTF-8');
}

/**
 * Vlož sem svůj reálný TMDB API klíč.
 */
$tmdb_api_key = 'VLOZ_SVUJ_TMDB_API_KLIC';

/**
 * Tajný token pro spuštění cron endpointu.
 */
$cron_secret_token = 'moje_heslo';

$errorLogFile = __DIR__ . '/cron_errors.log';

/**
 * Zaloguje chybu do cron_errors.log.
 */
function logCronError(string $message, string $errorLogFile): void
{
    $line = sprintf("[%s] %s\n", date('Y-m-d H:i:s'), $message);
    error_log($line, 3, $errorLogFile);
}

/**
 * Vrátí token z URL nebo CLI argumentu (--token=...).
 */
function getProvidedToken(): string
{
    if (PHP_SAPI === 'cli') {
        global $argv;
        if (!is_array($argv)) {
            return '';
        }

        foreach ($argv as $argument) {
            if (str_starts_with($argument, '--token=')) {
                return (string) substr($argument, 8);
            }
        }

        return '';
    }

    return isset($_GET['token']) ? (string) $_GET['token'] : '';
}

$providedToken = getProvidedToken();
if ($providedToken === '' || !hash_equals($cron_secret_token, $providedToken)) {
    $message = 'Unauthorized access attempt: invalid token.';
    logCronError($message, $errorLogFile);
    http_response_code(403);
    echo "Neplatný token.\n";
    exit(1);
}

if ($tmdb_api_key === '' || $tmdb_api_key === 'VLOZ_SVUJ_TMDB_API_KLIC') {
    $message = 'TMDB API key is missing or placeholder value is used.';
    logCronError($message, $errorLogFile);
    echo "Chybí TMDB API klíč.\n";
    exit(1);
}

require __DIR__ . '/../includes/db.php';

if (!$pdo instanceof PDO) {
    $message = 'DB connection failed' . (isset($dbError) && $dbError ? ': ' . $dbError : '.');
    logCronError($message, $errorLogFile);
    echo "DB connection failed.\n";
    exit(1);
}

$endpoint = 'https://api.themoviedb.org/3/movie/upcoming';
$query = http_build_query([
    'api_key' => $tmdb_api_key,
    'language' => 'cs-CZ',
    'region' => 'CZ',
    'page' => 1,
]);
$url = $endpoint . '?' . $query;

$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_CONNECTTIMEOUT => 15,
    CURLOPT_TIMEOUT => 45,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_HTTPGET => true,
]);

$responseBody = curl_exec($ch);
$curlError = curl_error($ch);
$httpCode = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($responseBody === false) {
    logCronError('cURL request failed: ' . $curlError, $errorLogFile);
    echo "Stahování z TMDB selhalo.\n";
    exit(1);
}

if ($httpCode !== 200) {
    $bodyPreview = mb_substr((string) $responseBody, 0, 300);
    logCronError("TMDB API HTTP {$httpCode}. Response: {$bodyPreview}", $errorLogFile);
    echo "TMDB API vrátilo HTTP {$httpCode}.\n";
    exit(1);
}

$data = json_decode((string) $responseBody, true);
if (!is_array($data) || !isset($data['results']) || !is_array($data['results'])) {
    logCronError('Invalid TMDB response format.', $errorLogFile);
    echo "Neplatný formát dat z TMDB.\n";
    exit(1);
}

$topMovies = array_slice($data['results'], 0, 20);

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

foreach ($topMovies as $movie) {
    if (!is_array($movie)) {
        continue;
    }

    $title = trim((string) ($movie['title'] ?? ''));
    $releaseDate = (string) ($movie['release_date'] ?? '');
    $externalId = isset($movie['id']) ? (string) $movie['id'] : '';

    if ($title === '' || $releaseDate === '' || $externalId === '') {
        continue;
    }

    $overview = trim((string) ($movie['overview'] ?? ''));
    $note = mb_substr($overview, 0, 500);

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

echo "Synchronizace dokončena. Uloženo/aktualizováno: {$savedCount} filmů.\n";
