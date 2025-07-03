package com.lambdar.ystudia.service;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.util.StreamUtils;
import org.springframework.web.multipart.MultipartFile;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class EmailService {

    private final JavaMailSender mailSender;
    private final TemplateEngine templateEngine;

    @Value("${spring.mail.username}")
    private String fromEmail;

    @Value("${app.frontend-url}")
    private String frontendUrl;
    private final String companyName = "Nexus Assets";


    @Async
    public void sendPasswordResetEmail(String toEmail, String token,String firstName) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject("Password Reset Request");

            Context context = new Context();
            context.setVariable("token", token);
            context.setVariable("resetUrl", frontendUrl + "/set-new-password?token=" + token);
            context.setVariable("userName", firstName);
            context.setVariable("frontendUrl", frontendUrl);

            String htmlContent = templateEngine.process("password-reset-email", context);
            helper.setText(htmlContent, true);

            mailSender.send(message);
            log.info("Password reset email sent to: {}", toEmail);
        } catch (MessagingException e) {
            log.error("Failed to send password reset email to {}: {}", toEmail, e.getMessage());
        }
    }

    public void sendWelcomeEmailWithPasswordSetup(String email, String firstName, String resetToken) {
        try {
            MimeMessage mimeMessage = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(mimeMessage, true, "UTF-8");

            helper.setTo(email);
            helper.setFrom(fromEmail);
            helper.setSubject("Welcome to " + companyName + " - Set Up Your Password");

            String setupUrl = frontendUrl + "/set-new-password?token=" + resetToken;
            String htmlContent = getWelcomeEmailTemplate()
                    .replace("[FIRST_NAME]", firstName)
                    .replace("[EMAIL]", email)
                    .replace("[SETUP_URL]", setupUrl)
                    .replace("[FRONTEND_URL]", frontendUrl)
                    .replace("[COMPANY_NAME]", companyName);

            helper.setText(htmlContent, true);

            mailSender.send(mimeMessage);

            log.info("Welcome email sent to: {}", email);
        } catch (Exception e) {
            log.error("Failed to send welcome email to: {}", email, e);
            // Fallback to simple text email
            sendWelcomeEmailFallback(email, firstName, resetToken);
        }
    }

    private void sendWelcomeEmailFallback(String email, String firstName, String resetToken) {
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setTo(email);
            message.setFrom(fromEmail);
            message.setSubject("Welcome to " + companyName + " - Set Up Your Password");

            String setupUrl = frontendUrl + "/set-password?token=" + resetToken;
            String content = "Hello " + firstName + ",\n\n" +
                    "Welcome to " + companyName + "! Your account has been created by an administrator.\n\n" +
                    "To get started, you need to set up your password. Please click the link below:\n\n" +
                    setupUrl + "\n\n" +
                    "This link will expire in 7 days. Once you set your password, you'll be able to log in using:\n" +
                    "Email: " + email + "\n" +
                    "Password: [The password you create]\n\n" +
                    "After setting up your password, you can log in at: " + frontendUrl + "/login\n\n" +
                    "If you have any questions, please contact your administrator.\n\n" +
                    "Best regards,\n" +
                    companyName + " Team";

            message.setText(content);
            mailSender.send(message);

            log.info("Welcome email (fallback) sent to: {}", email);
        } catch (Exception e) {
            log.error("Failed to send welcome email fallback to: {}", email, e);
            throw new RuntimeException("Failed to send welcome email");
        }
    }

    private String getWelcomeEmailTemplate() {
        try {
            ClassPathResource resource = new ClassPathResource("templates/welcome-email.html");
            return StreamUtils.copyToString(resource.getInputStream(), StandardCharsets.UTF_8);
        } catch (Exception e) {
            log.warn("Could not load welcome email template, using embedded template", e);
            return getEmbeddedWelcomeTemplate();
        }
    }
    private String getEmbeddedWelcomeTemplate() {
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to [COMPANY_NAME]</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; background-color: #f4f7fa; padding: 20px; }
        .email-container { max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 40px 30px; text-align: center; }
        .logo { font-size: 32px; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .logo-icon { width: 40px; height: 40px; background: linear-gradient(45deg, #27ae60, #2ecc71); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .subtitle { font-size: 18px; opacity: 0.9; font-weight: 300; }
        .content { padding: 40px 30px; }
        .greeting { font-size: 24px; color: #2c3e50; margin-bottom: 20px; font-weight: 600; }
        .welcome-text { color: #555; font-size: 16px; margin-bottom: 30px; line-height: 1.7; }
        .highlight-box { background: linear-gradient(135deg, #e8f5e8 0%, #f0f9f0 100%); border-left: 4px solid #27ae60; padding: 25px; margin: 30px 0; border-radius: 8px; }
        .highlight-title { font-size: 18px; font-weight: 600; color: #2c3e50; margin-bottom: 15px; }
        .cta-button { display: inline-block; background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); color: white; text-decoration: none; padding: 16px 32px; border-radius: 50px; font-size: 16px; font-weight: 600; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3); margin: 20px 0; }
        .button-container { text-align: center; margin: 30px 0; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }
        .info-card { background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; }
        .info-title { font-weight: 600; color: #2c3e50; margin-bottom: 8px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
        .info-value { color: #555; font-size: 16px; }
        .warning-box { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 30px 0; }
        .warning-text { color: #856404; font-size: 14px; display: flex; align-items: center; }
        .warning-icon { color: #f39c12; font-size: 20px; margin-right: 10px; }
        .footer { background: #f8fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0; }
        .footer-text { color: #64748b; font-size: 14px; margin-bottom: 15px; }
        .contact-info { color: #3498db; font-size: 14px; text-decoration: none; }
        @media (max-width: 600px) {
            .email-container { margin: 10px; border-radius: 8px; }
            .header, .content, .footer { padding: 25px 20px; }
            .info-grid { grid-template-columns: 1fr; }
            .greeting { font-size: 20px; }
            .logo { font-size: 28px; }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">🧠</div>
                [COMPANY_NAME]
            </div>
            <div class="subtitle">Intelligent Solutions Platform</div>
        </div>
        
        <div class="content">
            <div class="greeting">Welcome, [FIRST_NAME]!</div>
            
            <div class="welcome-text">
                We're excited to have you join the [COMPANY_NAME] team! Your account has been successfully created by your administrator, and you're just one step away from accessing our platform.
            </div>
            
            <div class="highlight-box">
                <div class="highlight-title">🔐 Account Setup Required</div>
                <p>To secure your account and get started, you'll need to create your password. This is a one-time setup process that ensures your account remains safe and secure.</p>
            </div>
            
            <div class="button-container">
                <a href="[SETUP_URL]" class="cta-button">Set Up Password</a>
            </div>
            
            <div class="info-grid">
                <div class="info-card">
                    <div class="info-title">Your Email</div>
                    <div class="info-value">[EMAIL]</div>
                </div>
                <div class="info-card">
                    <div class="info-title">Login URL</div>
                    <div class="info-value">[FRONTEND_URL]/login</div>
                </div>
            </div>
            
            <div class="warning-box">
                <div class="warning-text">
                    <span class="warning-icon">⚠️</span>
                    <span>This password setup link will expire in 7 days. If you don't set up your password within this time, please contact your administrator for assistance.</span>
                </div>
            </div>
            
            <div class="welcome-text">
                Once you've set up your password, you'll have full access to all the features and tools available in [COMPANY_NAME]. If you have any questions or need assistance, don't hesitate to reach out to your administrator or our support team.
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-text">
                Need help? Contact your administrator or reach out to our support team.
            </div>
            <a href="mailto:support@greenbrain.nexus" class="contact-info">support@greenbrain.nexus</a>
            
            <div style="margin-top: 20px; font-size: 12px; color: #94a3b8;">
                © 2024 [COMPANY_NAME]. All rights reserved.<br>
                This email was sent to [EMAIL] because an administrator created an account for you.
            </div>
        </div>
    </div>
</body>
</html>
                """;
    }



    @Async
    public void sendEmailWithAttachment(String toEmail, String subject, String htmlContent,
                                        String attachmentPath, String attachmentName) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(htmlContent, true);

            // Add file attachment
            FileSystemResource file = new FileSystemResource(new File(attachmentPath));
            helper.addAttachment(attachmentName, file);

            mailSender.send(message);
            log.info("Email with attachment sent to: {}", toEmail);
        } catch (MessagingException e) {
            log.error("Failed to send email with attachment to {}: {}", toEmail, e.getMessage());
        }
    }

    @Async
    public void sendEmailWithMultipleAttachments(String toEmail, String subject, String htmlContent,
                                                 Map<String, String> attachments) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(htmlContent, true);

            // Add multiple file attachments
            for (Map.Entry<String, String> attachment : attachments.entrySet()) {
                String attachmentName = attachment.getKey();
                String attachmentPath = attachment.getValue();
                FileSystemResource file = new FileSystemResource(new File(attachmentPath));
                helper.addAttachment(attachmentName, file);
            }

            mailSender.send(message);
            log.info("Email with {} attachments sent to: {}", attachments.size(), toEmail);
        } catch (MessagingException e) {
            log.error("Failed to send email with attachments to {}: {}", toEmail, e.getMessage());
        }
    }

    @Async
    public void sendEmailWithByteArrayAttachment(String toEmail, String subject, String htmlContent,
                                                 byte[] attachmentData, String attachmentName) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(htmlContent, true);

            // Add byte array attachment
            ByteArrayResource byteArrayResource = new ByteArrayResource(attachmentData);
            helper.addAttachment(attachmentName, byteArrayResource);

            mailSender.send(message);
            log.info("Email with byte array attachment sent to: {}", toEmail);
        } catch (MessagingException e) {
            log.error("Failed to send email with byte array attachment to {}: {}", toEmail, e.getMessage());
        }
    }

    @Async
    public void sendEmailWithMultipartFileAttachment(String toEmail, String subject, String htmlContent,
                                                     MultipartFile file) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(htmlContent, true);

            // Add MultipartFile attachment
            ByteArrayResource byteArrayResource = new ByteArrayResource(file.getBytes());
            helper.addAttachment(file.getOriginalFilename(), byteArrayResource);

            mailSender.send(message);
            log.info("Email with multipart file attachment sent to: {}", toEmail);
        } catch (MessagingException | IOException e) {
            log.error("Failed to send email with multipart file attachment to {}: {}", toEmail, e.getMessage());
        }
    }

    @Async
    public void sendEmailWithMultipleMultipartFiles(String toEmail, String subject, String htmlContent,
                                                    List<MultipartFile> files) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(htmlContent, true);

            // Add multiple MultipartFile attachments
            for (MultipartFile file : files) {
                ByteArrayResource byteArrayResource = new ByteArrayResource(file.getBytes());
                helper.addAttachment(file.getOriginalFilename(), byteArrayResource);
            }

            mailSender.send(message);
            log.info("Email with {} multipart file attachments sent to: {}", files.size(), toEmail);
        } catch (MessagingException | IOException e) {
            log.error("Failed to send email with multipart file attachments to {}: {}", toEmail, e.getMessage());
        }
    }

    @Async
    public void sendTemplatedEmailWithAttachment(String toEmail, String subject, String templateName,
                                                 Context templateContext, String attachmentPath,
                                                 String attachmentName) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject(subject);

            // Process template
            String htmlContent = templateEngine.process(templateName, templateContext);
            helper.setText(htmlContent, true);

            // Add file attachment
            FileSystemResource file = new FileSystemResource(new File(attachmentPath));
            helper.addAttachment(attachmentName, file);

            mailSender.send(message);
            log.info("Templated email with attachment sent to: {}", toEmail);
        } catch (MessagingException e) {
            log.error("Failed to send templated email with attachment to {}: {}", toEmail, e.getMessage());
        }
    }

    @Async
    public void sendEmailWithResourceAttachment(String toEmail, String subject, String htmlContent,
                                                Resource attachment, String attachmentName) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(htmlContent, true);

            // Add Resource attachment (can be any Spring Resource)
            helper.addAttachment(attachmentName, attachment);

            mailSender.send(message);
            log.info("Email with resource attachment sent to: {}", toEmail);
        } catch (MessagingException e) {
            log.error("Failed to send email with resource attachment to {}: {}", toEmail, e.getMessage());
        }
    }
}