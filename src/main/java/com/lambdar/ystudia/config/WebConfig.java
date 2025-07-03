package com.lambdar.ystudia.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@EnableWebMvc
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/swagger-ui/**")
                .addResourceLocations("classpath:/META-INF/resources/webjars/springdoc-openapi-ui/")
                .resourceChain(false);
        registry.addResourceHandler("/icon/**")
                .addResourceLocations("classpath:static/icons/")
                .resourceChain(false);
        registry.addResourceHandler("/default/**")
                .addResourceLocations("classpath:static/defaults/")
                .resourceChain(false);
    }
}