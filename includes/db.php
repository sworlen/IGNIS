<?php

declare(strict_types=1);

$host = 'sql105.infinityfree.com';
$dbName = 'if0_41347982_Ignis';
$username = 'if0_41347982';
$password = 'Rebelka123XD';
$charset = 'utf8mb4';

$dsn = "mysql:host={$host};dbname={$dbName};charset={$charset}";
$options = [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false,
];

$pdo = null;
$dbError = null;

try {
    $pdo = new PDO($dsn, $username, $password, $options);
} catch (PDOException $exception) {
    $dbError = $exception->getMessage();
}
