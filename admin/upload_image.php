<?php

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

if (!isset($_FILES['file'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Nebyl odeslán žádný soubor.']);
    exit;
}

$file = $_FILES['file'];

if (($file['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) {
    http_response_code(400);
    echo json_encode(['error' => 'Nahrávání souboru selhalo.']);
    exit;
}

$allowedMimeTypes = [
    'image/jpeg' => 'jpg',
    'image/png' => 'png',
    'image/webp' => 'webp',
    'image/gif' => 'gif',
];

$finfo = new finfo(FILEINFO_MIME_TYPE);
$mimeType = $finfo->file($file['tmp_name']);

if (!isset($allowedMimeTypes[$mimeType])) {
    http_response_code(415);
    echo json_encode(['error' => 'Nepodporovaný formát obrázku.']);
    exit;
}

$uploadDir = __DIR__ . '/../assets/images';
if (!is_dir($uploadDir) && !mkdir($uploadDir, 0755, true) && !is_dir($uploadDir)) {
    http_response_code(500);
    echo json_encode(['error' => 'Nepodařilo se vytvořit cílovou složku.']);
    exit;
}

$extension = $allowedMimeTypes[$mimeType];
$filename = sprintf('img_%s.%s', bin2hex(random_bytes(8)), $extension);
$targetPath = $uploadDir . '/' . $filename;

if (!move_uploaded_file($file['tmp_name'], $targetPath)) {
    http_response_code(500);
    echo json_encode(['error' => 'Nepodařilo se uložit soubor.']);
    exit;
}

$imageUrl = '/assets/images/' . $filename;
echo json_encode(['location' => $imageUrl], JSON_UNESCAPED_SLASHES);
