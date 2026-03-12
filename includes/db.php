<?php

declare(strict_types=1);

$host = getenv('DB_HOST') ?: '127.0.0.1';
$dbName = getenv('DB_NAME') ?: 'ignis';
$username = getenv('DB_USER') ?: 'root';
$password = getenv('DB_PASSWORD') ?: '';
$charset = 'utf8mb4';

$dsn = "mysql:host={$host};dbname={$dbName};charset={$charset}";
$options = [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false,
];

/**
 * Vytvoří PDO připojení.
 */
function createPdoConnection(string $dsn, string $username, string $password, array $options): ?PDO
{
    try {
        return new PDO($dsn, $username, $password, $options);
    } catch (PDOException $exception) {
        error_log('Database connection error: ' . $exception->getMessage());
        return null;
    }
}

$pdo = createPdoConnection($dsn, $username, $password, $options);
