package com.lambdar.ystudia.service;

import com.google.cloud.storage.*;
import com.lambdar.ystudia.exception.UnAuthenticatedException;
import com.lambdar.ystudia.exception.UnSupportMediaType;
import com.lambdar.ystudia.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.Files;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;


@Slf4j
@Service
@RequiredArgsConstructor
public class FileService {
    private final Storage storage;
    private final JwtTokenProvider jwtTokenProvider;
    @Value("${app.base.url}")
    private String baseUrl;
    @Value("${spring.cloud.gcp.storage.bucket-name:nexusasm}")
    private String bucketName;
    public String getFileExtension(String filename) {
        if (filename != null && filename.contains(".")) {
            return filename.substring(filename.lastIndexOf("."));
        }
        return "";
    }
    public static enum FileType {
        IMAGE,DOCUMENT
    }

    public String uploadFile(InputStream inputStream,GCSSubFolder subFolder, String filename) throws IOException{
        byte[] fileBytes = inputStream.readAllBytes();
        long fileSize = fileBytes.length;
        String newFilename = UUID.randomUUID().toString() + getFileExtension(filename);
        String subDir = String.format("%s/%S",subFolder,newFilename);
        String contentType = Files.probeContentType(new File(newFilename).toPath());
        String storagePath = String.format("%s/%s", bucketName, subDir);
        Map<String, String> metadata = new HashMap<>();
        metadata.put("filename", filename);
        metadata.put("content-type", contentType);
        metadata.put("content-length", String.valueOf(fileSize));

        BlobInfo blobInfo = BlobInfo
                .newBuilder(bucketName, storagePath)
                .setContentType(contentType)
                .setMetadata(metadata)
                .build();

        final Blob blob = storage.create(blobInfo, fileBytes);
        if (blob != null && !blob.getContentType().isBlank()) {
            return subDir;
        }
        return "";
    }

    public Blob downloadFileWithSignToken(String token) {
        if(!jwtTokenProvider.validateToken(token)){
            throw new UnAuthenticatedException("You need full authentication to access resource");
        }
        String filename = jwtTokenProvider.getfilename(token);
        return downloadFile(filename);
    }
    public Blob downloadFile(String filename) {
        String storagePath = String.format("%s/%s", bucketName, filename);
        Blob blob = storage.get(BlobId.of(bucketName, storagePath));
        if (blob == null) {
            throw new IllegalArgumentException("File not found in bucket: " + filename);
        }
        return blob;
    }

    public String convertToSignUrl(String filename){
        if(filename == null || filename.isEmpty()){
            return "";
        }
        String token = jwtTokenProvider.createAccessToken(filename);
        return String.format("%s/file/%s",baseUrl,token);
    }

    public void deleteFile(String filename) {
        try {
            String storagePath = String.format("%s/%s", bucketName, filename);

            var blobId = BlobInfo
                    .newBuilder(bucketName, storagePath)
                    .build().getBlobId();

            boolean deleted = storage.delete(blobId);
            log.info("File [{}] deleted [{}]", filename, deleted ? "successfully" : "failed");

        } catch (Exception ex) {
            log.error("Error Occurred: [{}]", ex.getMessage(), ex);
        }
    }
    public enum GCSSubFolder{
        ASSET,PROFILE,ASSET_TRANSFER
    }
}
