package com.lambdar.ystudia.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;


@Configuration
public class GoogleCloudStorage {
    @Bean
    public Storage storage(){
        return StorageOptions.getDefaultInstance().getService();
    }
}
