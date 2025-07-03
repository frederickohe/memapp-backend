package com.lambdar.ystudia.notification.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.lambdar.ystudia.notification.dto.NotificationDto;
import com.lambdar.ystudia.notification.service.NotificationService;
import com.lambdar.ystudia.dto.response.MessageResponse;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/v1/notifications")
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    @GetMapping
    public ResponseEntity<List<NotificationDto>> getAllNotifications() {
        return ResponseEntity.ok(notificationService.getAllUserNotifications());
    }

    @GetMapping("/{id}")
    public ResponseEntity<NotificationDto> getNotificationById(@PathVariable Long id) {
        NotificationDto dto = notificationService.getNotificationById(id);
        return ResponseEntity.ok(dto);
    }

    @PostMapping
    public ResponseEntity<MessageResponse> createNotification(@RequestBody NotificationDto notificationDto) {
        MessageResponse response = notificationService.createNotification(notificationDto);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{id}/read")
    public ResponseEntity<MessageResponse> markAsRead(@PathVariable Long id) {
        MessageResponse response = notificationService.markAsRead(id);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<MessageResponse> deleteNotification(@PathVariable Long id) {
        MessageResponse response = notificationService.deleteNotification(id);
        return ResponseEntity.ok(response);
    }
}
