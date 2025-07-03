package com.lambdar.ystudia.dto.response;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class DataSaveMessage<T> {
    private String message;
    private T data;
}
