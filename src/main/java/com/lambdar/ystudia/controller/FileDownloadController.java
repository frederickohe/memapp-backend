package com.lambdar.ystudia.controller;

import com.google.cloud.storage.Blob;
import com.lambdar.ystudia.service.FileService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/file")
public class FileDownloadController {
    private final FileService fileService;
    @GetMapping("/{token}")
    public ResponseEntity<?> getFile(@PathVariable String token){
        Blob blob = fileService.downloadFileWithSignToken(token);
        String filename = blob.getMetadata().get("filename");
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(blob.getContentType()))
                .contentLength(blob.getSize())
                .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + filename + "\"")
                .body(blob.getContent());
    }
}
