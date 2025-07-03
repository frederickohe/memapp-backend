package com.lambdar.ystudia.auth.service;

import java.time.LocalDateTime;
import java.util.UUID;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.lambdar.ystudia.auth.dto.request.LoginRequest;
import com.lambdar.ystudia.auth.dto.request.RefreshTokenRequest;
import com.lambdar.ystudia.user.dto.request.RegisterRequest;
import com.lambdar.ystudia.dto.response.JwtResponse;
import com.lambdar.ystudia.dto.response.MessageResponse;
import com.lambdar.ystudia.exception.DuplicateResourceException;
import com.lambdar.ystudia.exception.ResourceNotFoundException;
import com.lambdar.ystudia.exception.TokenRefreshException;
import com.lambdar.ystudia.exception.UnAuthenticatedException;
import com.lambdar.ystudia.auth.model.PasswordResetToken;
import com.lambdar.ystudia.auth.model.RefreshToken;
import com.lambdar.ystudia.auth.repository.PasswordResetTokenRepository;
import com.lambdar.ystudia.user.repository.UserRepository;
import com.lambdar.ystudia.repository.UserRoleRepository;
import com.lambdar.ystudia.security.JwtTokenProvider;
import com.lambdar.ystudia.service.EmailService;
import com.lambdar.ystudia.user.model.User;
import com.lambdar.ystudia.user.model.UserRole;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class AuthService {
    private static final Logger logger = LoggerFactory.getLogger(AuthService.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenService refreshTokenService;
    private final UserRoleRepository userRoleRepository;
    private final PasswordResetTokenRepository passwordResetTokenRepository;
    private final EmailService emailService;

    private UserRole getUserRole(Long id){
        return userRoleRepository.findById(id).orElseThrow(()->new ResourceNotFoundException("User role not found"));
    }


    @Transactional
    public JwtResponse login(LoginRequest loginRequest) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(loginRequest.getEmail(), loginRequest.getPassword()));

        User userDetails = (User) authentication.getPrincipal();

        if (!userDetails.isEnabled()) {
            throw new UnAuthenticatedException("User account is disabled");
        }

        SecurityContextHolder.getContext().setAuthentication(authentication);
        String accessToken = jwtTokenProvider.createAccessToken(authentication);

        RefreshToken refreshToken = refreshTokenService.createRefreshToken(userDetails.getUsername());

        return JwtResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken.getToken())
                .tokenType("Bearer")
                .id(userDetails.getId())
                .email(userDetails.getEmail())
                .firstName(userDetails.getFirstName())
                .lastName(userDetails.getLastName())
                .build();
    }


    @Transactional
    public JwtResponse refreshToken(RefreshTokenRequest request) {
        String requestRefreshToken = request.getRefreshToken();

        return refreshTokenService.findByToken(requestRefreshToken)
                .map(refreshTokenService::verifyExpiration)
                .map(RefreshToken::getUser)
                .map(user -> {
                    String accessToken = jwtTokenProvider.createAccessTokenFromUsername(user.getUsername());

                    return JwtResponse.builder()
                            .accessToken(accessToken)
                            .refreshToken(requestRefreshToken)
                            .tokenType("Bearer")
                            .id(user.getId())
                            .email(user.getUsername())
                            .firstName(user.getFirstName())
                            .lastName(user.getLastName())
                            .build();
                })
                .orElseThrow(() -> new TokenRefreshException(requestRefreshToken,
                        "Refresh token is not found in database!"));
    }

    @Transactional
    public MessageResponse register(RegisterRequest registerRequest) {

        try {
            if (userRepository.existsByEmail(registerRequest.getEmail())) {
                throw new DuplicateResourceException("Email is already in use!");
            }

            logger.info("Role id " + registerRequest.getRoleId());
            logger.info(String.valueOf(registerRequest));

            UserRole userRole = getUserRole(registerRequest.getRoleId());

            String temporaryPassword = generateRandomPassword();

            User user = User.builder()
                    .email(registerRequest.getEmail())
                    .hashedPassword(passwordEncoder.encode(temporaryPassword))
                    .firstName(registerRequest.getFirstName())
                    .lastName(registerRequest.getLastName())
                    .phone(registerRequest.getPhone())
                    .createdAt(LocalDateTime.now())
                    .userRole(userRole)
                    .enabled(false)
                    .build();


            user = userRepository.saveAndFlush(user);


            String resetToken = UUID.randomUUID().toString();

            passwordResetTokenRepository.deleteByUser(user);

            PasswordResetToken passwordResetToken = PasswordResetToken.builder()
                    .token(resetToken)
                    .user(user)
                    .expiryDate(LocalDateTime.now().plusDays(7))
                    .build();

            passwordResetTokenRepository.save(passwordResetToken);

            emailService.sendWelcomeEmailWithPasswordSetup(
                    user.getEmail(),
                    user.getFirstName(),
                    resetToken
            );

            return new MessageResponse("User registered successfully! An email has been sent to set up their password.");

        } catch (DataIntegrityViolationException e) {
            System.out.println(e);
            throw new RuntimeException("Registration failed due to data constraints: " + e.getMostSpecificCause().getMessage());
        } catch (Exception e) {
            System.out.println(e);
            e.printStackTrace();
            throw new RuntimeException("Registration failed: " + e.getMessage());
        }
    }

    @Transactional
    public MessageResponse logout(RefreshTokenRequest request) {
        return refreshTokenService.findByToken(request.getRefreshToken())
                .map(token -> {
                    refreshTokenService.revokeAllUserTokens(token.getUser());
                    return new MessageResponse("Logout successful!");
                })
                .orElseThrow(() -> new TokenRefreshException(request.getRefreshToken(),
                        "Refresh token is not found in database!"));
    }

    private String generateRandomPassword() {
        return UUID.randomUUID().toString().substring(0, 12);
    }
}