package com.lambdar.ystudia.auth.service;

import java.time.LocalDateTime;
import java.util.UUID;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.lambdar.ystudia.auth.dto.request.ForgotPasswordRequest;
import com.lambdar.ystudia.auth.dto.request.ResetPasswordRequest;
import com.lambdar.ystudia.dto.response.MessageResponse;
import com.lambdar.ystudia.exception.ResourceNotFoundException;
import com.lambdar.ystudia.exception.UnAuthenticatedException;
import com.lambdar.ystudia.auth.model.PasswordResetToken;
import com.lambdar.ystudia.user.model.User;
import com.lambdar.ystudia.user.repository.UserRepository;
import com.lambdar.ystudia.service.EmailService;
import com.lambdar.ystudia.auth.repository.PasswordResetTokenRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class PasswordResetService {

    private final UserRepository userRepository;
    private final PasswordResetTokenRepository passwordResetTokenRepository;
    private final PasswordEncoder passwordEncoder;
    private final EmailService emailService;

    @Transactional
    public MessageResponse requestPasswordReset(ForgotPasswordRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new ResourceNotFoundException("User not found with email: " + request.getEmail()));

        String token = generateResetToken();

        passwordResetTokenRepository.deleteByUser(user);

        PasswordResetToken resetToken = PasswordResetToken.builder()
                .token(token)
                .user(user)
                .expiryDate(LocalDateTime.now().plusHours(1))
                .build();

        passwordResetTokenRepository.save(resetToken);

        emailService.sendPasswordResetEmail(user.getEmail(),user.getFirstName(), token);

        return new MessageResponse("Password reset instructions have been sent to your email.");
    }

    @Transactional
    public MessageResponse resetPassword(ResetPasswordRequest request) {
        PasswordResetToken resetToken = passwordResetTokenRepository.findByToken(request.getToken())
                .orElseThrow(() -> new UnAuthenticatedException("Invalid password reset token"));

        if (resetToken.isExpired()) {
            throw new UnAuthenticatedException("Password reset token is expired");
        }

        User user = resetToken.getUser();
        user.setHashedPassword(passwordEncoder.encode(request.getNewPassword()));

        if (!user.isEnabled()) {
            user.setEnabled(true);
            log.info("Enabling user account for: {}", user.getEmail());
        }

        userRepository.save(user);

        resetToken.setUsed(true);
        passwordResetTokenRepository.save(resetToken);

        return new MessageResponse("Password has been set successfully. You can now log in.");
    }

    private String generateResetToken() {
        return UUID.randomUUID().toString();
    }
}