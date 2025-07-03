package com.lambdar.ystudia.notification.service;

import java.util.List;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.lambdar.ystudia.notification.dto.NotificationDto;
import com.lambdar.ystudia.notification.model.Notification;
import com.lambdar.ystudia.notification.repository.NotificationRepository;
import com.lambdar.ystudia.user.repository.UserRepository;
import com.lambdar.ystudia.dto.response.MessageResponse;
import com.lambdar.ystudia.user.model.User;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class NotificationService {
    
    private final UserRepository userRepository;
    private final NotificationRepository notificationRepository;

    public List<NotificationDto> getAllUserNotifications() {
        User currentUser = getCurrentUser();
        List<Notification> notifications = notificationRepository.findAllByUserEmail(currentUser.getEmail());
        return notifications.stream()
                .map(this::toDto)
                .toList();
    }

    // Helper method to map Notification entity to NotificationDto
    private NotificationDto toDto(Notification notification) {
        // Map fields as appropriate
        NotificationDto dto = new NotificationDto();
        dto.setId(notification.getId());
        dto.setTitle(notification.getTitle());
        dto.setMessage(notification.getMessage());
        dto.setRead(notification.isRead());
        dto.setCreatedAt(notification.getCreatedAt());

        return dto;
    }

    public MessageResponse markAsRead(Long id) {
        User currentUser = getCurrentUser();
        Notification notification = notificationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Notification not found"));
        if (!notification.getUser().getId().equals(currentUser.getId())) {
            throw new RuntimeException("Unauthorized to mark this notification as read");
        }
        if (!notification.isRead()) {
            notification.setRead(true);
            notificationRepository.save(notification);
            return new MessageResponse("Notification marked as read.");
        } else {
            return new MessageResponse("Notification was already marked as read.");
        }
    }

    public NotificationDto getNotificationById(Long id) {
        User currentUser = getCurrentUser();
        Notification notification = notificationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Notification not found"));
        if (!notification.getUser().getId().equals(currentUser.getId())) {
            throw new RuntimeException("Unauthorized to access this notification");
        }
        return toDto(notification);
    }

    public MessageResponse createNotification(NotificationDto notificationDto) {
        User currentUser = getCurrentUser();
        Notification notification = new Notification();
        notification.setUser(currentUser);
        notification.setTitle(notificationDto.getTitle());
        notification.setMessage(notificationDto.getMessage());
        notification.setRead(false);
        notification.setCreatedAt(notificationDto.getCreatedAt() != null ? notificationDto.getCreatedAt() : java.time.LocalDateTime.now());
        notificationRepository.save(notification);
        return new MessageResponse("Notification created successfully.");
    }

    public MessageResponse deleteNotification(Long id) {
        User currentUser = getCurrentUser();
        Notification notification = notificationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Notification not found"));
        if (!notification.getUser().getId().equals(currentUser.getId())) {
            throw new RuntimeException("Unauthorized to delete this notification");
        }
        notificationRepository.delete(notification);
        return new MessageResponse("Notification deleted successfully.");
    }

    private User getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String userEmail = authentication.getName();

        return userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }
}