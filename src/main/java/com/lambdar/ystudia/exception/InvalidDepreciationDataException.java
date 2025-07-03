package com.lambdar.ystudia.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.BAD_REQUEST)
public class InvalidDepreciationDataException extends RuntimeException {
    public InvalidDepreciationDataException(String message) {
        super(message);
    }
}
